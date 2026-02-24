import { useState } from 'react'
import './BulkUploadTable.css'

const STATUS_EXACT = 'exact'
const STATUS_FUZZY = 'fuzzy'
const STATUS_NOT_FOUND = 'not_found'

function StatusIcon({ status }) {
  if (status === STATUS_NOT_FOUND) {
    return (
      <span className="bulk-status-icon bulk-status-icon--error" title="Не найдено" aria-hidden>
        ✕
      </span>
    )
  }
  if (status === STATUS_FUZZY) {
    return (
      <span className="bulk-status-icon bulk-status-icon--warn" title="Неточное совпадение" aria-hidden>
        !
      </span>
    )
  }
  return (
    <span className="bulk-status-icon bulk-status-icon--ok" title="Совпадение" aria-hidden>
      ✓
    </span>
  )
}

export default function BulkUploadTable({ rows = [], onRowsChange, zones = [], models = [], onConfirm, confirmLoading = false, confirmError = null }) {
  const [localError, setLocalError] = useState(null)
  const [localWarning, setLocalWarning] = useState(null)

  const handleSelectModel = (rowIndex, modelId) => {
    const value = modelId === '' ? null : Number(modelId)
    const next = rows.map((r, i) =>
      i === rowIndex ? { ...r, matched_id: value, status: value ? 'manual' : STATUS_NOT_FOUND, confidence: value ? 100 : 0 } : r
    )
    onRowsChange?.(next)
  }

  const getZoneId = (originalZone) => {
    const name = (originalZone || '').trim()
    const z = zones.find((zone) => zone.name === name)
    return z?.id ?? null
  }

  const handleConfirm = () => {
    setLocalError(null)
    setLocalWarning(null)
    const withZone = rows
      .filter((r) => r.matched_id != null && r.matched_id !== '')
      .map((r) => ({
        matched_id: r.matched_id,
        zone_id: getZoneId(r.original_zone),
      }))
      .filter((r) => r.zone_id != null)
    const missingZone = rows.filter((r) => r.matched_id != null && getZoneId(r.original_zone) == null)
    const noModel = rows.filter((r) => r.matched_id == null || r.matched_id === '')
    if (withZone.length === 0) {
      setLocalError(
        missingZone.length > 0
          ? 'У всех строк с выбранной моделью не удалось определить зону по названию. Проверьте колонку «Зона защиты» или выберите модель для строк «Не найдено».'
          : noModel.length === rows.length
            ? 'Выберите модель хотя бы в одной строке или загрузите другой файл.'
            : 'Нет строк с выбранной моделью и известной зоной.'
      )
      return
    }
    const parts = []
    if (withZone.length > 0) parts.push(`Будут сохранены расчёты по ${withZone.length} строкам`)
    if (noModel.length > 0) parts.push(noModel.length === 1 ? '1 строка без выбранной модели не войдёт в сохранение' : `${noModel.length} строк без выбранной модели не войдут в сохранение`)
    if (missingZone.length > 0) parts.push(missingZone.length === 1 ? '1 строка без распознанной зоны не войдёт в сохранение' : `${missingZone.length} строк без распознанной зоны не войдут в сохранение`)
    setLocalWarning(parts.length > 0 ? parts.join('. ') : null)
    onConfirm?.(withZone)
  }

  const canConfirm = rows.some((r) => r.matched_id != null) && !confirmLoading

  if (rows.length === 0) {
    return null
  }

  return (
    <div className="bulk-upload-table-wrap">
      <table className="bulk-upload-table">
        <thead>
          <tr>
            <th>Техника (из файла)</th>
            <th>Зона защиты</th>
            <th>Статус</th>
            <th>Совпадение / выбор</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx} className={row.status === STATUS_NOT_FOUND ? 'bulk-row--not-found' : ''}>
              <td>{row.original_text || '—'}</td>
              <td>{row.original_zone || '—'}</td>
              <td>
                <StatusIcon status={row.status} />
                {row.status === STATUS_EXACT && ' Точное'}
                {row.status === STATUS_FUZZY && ` Неточное (${row.confidence}%)`}
                {row.status === STATUS_NOT_FOUND && ' Не найдено'}
                {row.status === 'manual' && ' Выбрано вручную'}
              </td>
              <td>
                {row.status === STATUS_NOT_FOUND ? (
                  <select
                    value={row.matched_id ?? ''}
                    onChange={(e) => handleSelectModel(idx, e.target.value)}
                    className="bulk-select-model"
                    aria-label="Выбор модели"
                  >
                    <option value="">— Выберите модель —</option>
                    {models.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span>
                    {row.matched_id != null ? `ID ${row.matched_id}` : '—'} {row.confidence != null && row.confidence > 0 ? `(${row.confidence}%)` : ''}
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="bulk-actions">
        {localWarning && (
          <div className="bulk-message bulk-message--warn" role="status">{localWarning}</div>
        )}
        {(localError || confirmError) && (
          <div className="bulk-message bulk-message--error">{localError || confirmError}</div>
        )}
        <button
          type="button"
          className="bulk-btn-confirm"
          onClick={handleConfirm}
          disabled={!canConfirm}
        >
          {confirmLoading ? 'Создание…' : 'Подтвердить и создать расчёты'}
        </button>
      </div>
    </div>
  )
}
