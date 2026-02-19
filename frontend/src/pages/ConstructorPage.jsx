import { useState, useEffect, useCallback } from 'react'
import { searchModels, getZones, calculate, saveCalculation } from '../api'
import './ConstructorPage.css'

const DEBOUNCE_MS = 300

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debouncedValue
}

export default function ConstructorPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [zones, setZones] = useState([])
  const [selectedZoneIds, setSelectedZoneIds] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null)
  const [error, setError] = useState(null)

  const debouncedSearch = useDebounce(searchQuery, DEBOUNCE_MS)

  // Загрузка зон при монтировании
  useEffect(() => {
    getZones()
      .then(setZones)
      .catch((e) => setError(e.message))
  }, [])

  // Live-search по модификациям
  useEffect(() => {
    if (!debouncedSearch.trim()) {
      setSearchResults([])
      return
    }
    searchModels(debouncedSearch.trim())
      .then(setSearchResults)
      .catch(() => setSearchResults([]))
  }, [debouncedSearch])

  // Расчёт при смене модели или зон
  const runCalculate = useCallback(async () => {
    if (!selectedModel) {
      setResult(null)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await calculate(selectedModel.id, selectedZoneIds)
      setResult(data)
    } catch (e) {
      setError(e.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }, [selectedModel, selectedZoneIds])

  useEffect(() => {
    runCalculate()
  }, [runCalculate])

  const toggleZone = (zoneId) => {
    setSelectedZoneIds((prev) =>
      prev.includes(zoneId) ? prev.filter((id) => id !== zoneId) : [...prev, zoneId]
    )
  }

  const handleSave = async () => {
    if (!selectedModel || !result) return
    setSaveStatus(null)
    setError(null)
    try {
      const data = await saveCalculation(selectedModel.id, selectedZoneIds, result.total_price)
      setSaveStatus(`Расчёт сохранён, id: ${data.id}`)
    } catch (e) {
      setError(e.message)
      setSaveStatus(null)
    }
  }

  return (
    <div className="constructor">
      <header className="constructor-header">
        <h1>Конструктор комплектации</h1>
      </header>

      <div className="constructor-layout">
        <aside className="constructor-sidebar">
          <div className="sidebar-block">
            <label htmlFor="search">Поиск техники</label>
            <input
              id="search"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Название или синоним..."
              autoComplete="off"
            />
            <ul className="model-list" aria-label="Результаты поиска">
              {searchResults.map((m) => (
                <li
                  key={m.id}
                  className={selectedModel?.id === m.id ? 'selected' : ''}
                  onClick={() => setSelectedModel(m)}
                  onKeyDown={(e) => e.key === 'Enter' && setSelectedModel(m)}
                  role="button"
                  tabIndex={0}
                >
                  {m.name}
                </li>
              ))}
            </ul>
            {selectedModel && (
              <p className="selected-model">Выбрано: {selectedModel.name}</p>
            )}
          </div>

          <div className="sidebar-block">
            <span className="sidebar-title">Зоны защиты</span>
            {zones.map((z) => (
              <label key={z.id} className="zone-checkbox">
                <input
                  type="checkbox"
                  checked={selectedZoneIds.includes(z.id)}
                  onChange={() => toggleZone(z.id)}
                />
                {z.name}
              </label>
            ))}
          </div>
        </aside>

        <main className="constructor-main">
          {error && <div className="message error">{error}</div>}
          {saveStatus && <div className="message success">{saveStatus}</div>}

          {loading && <p className="loading">Расчёт…</p>}

          {result && !loading && (
            <>
              <section className="result-spec">
                <h2>Итоговая спецификация</h2>
                {Object.entries(result.groups || {}).map(([typeName, items]) => (
                  <div key={typeName} className="spec-group">
                    <h3>{typeName}</h3>
                    <ul>
                      {items.map((item) => (
                        <li key={item.id}>
                          {item.name} — {item.price.toLocaleString('ru-RU')} ₽
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </section>

              <div className="result-total">
                <strong>Итоговая цена: {result.total_price.toLocaleString('ru-RU')} ₽</strong>
              </div>

              <button
                type="button"
                className="btn-save"
                onClick={handleSave}
              >
                Сохранить расчёт
              </button>
            </>
          )}

          {!result && !loading && selectedModel && (
            <p className="hint">Выберите зоны и дождитесь расчёта</p>
          )}
          {!selectedModel && (
            <p className="hint">Введите поиск и выберите модель техники</p>
          )}
        </main>
      </div>
    </div>
  )
}
