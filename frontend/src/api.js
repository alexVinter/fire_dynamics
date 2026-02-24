/**
 * API клиент для backend (Модуль 3).
 * Base URL из VITE_API_URL (в Docker: http://localhost:8000).
 */
const BASE = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || ''

export async function searchModels(search) {
  const q = search ? `?search=${encodeURIComponent(search)}` : ''
  const r = await fetch(`${BASE}/api/models/${q}`)
  if (!r.ok) throw new Error('Ошибка поиска моделей')
  return r.json()
}

export async function getZones() {
  const r = await fetch(`${BASE}/api/zones/`)
  if (!r.ok) throw new Error('Ошибка загрузки зон')
  return r.json()
}

export async function calculate(modelId, zoneIds) {
  const r = await fetch(`${BASE}/api/calculate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_id: modelId, zone_ids: zoneIds }),
  })
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Ошибка расчёта')
  return data
}

export async function saveCalculation(modelId, zoneIds, totalPrice) {
  const r = await fetch(`${BASE}/api/calculations/save/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model_id: modelId,
      zone_ids: zoneIds,
      total_price: totalPrice,
    }),
  })
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Ошибка сохранения')
  return data
}

/** Список всех моделей (для выпадающего списка). */
export async function getAllModels() {
  const r = await fetch(`${BASE}/api/models/`)
  if (!r.ok) throw new Error('Ошибка загрузки моделей')
  return r.json()
}

function parseJsonOrThrow(r, fallbackMessage) {
  return r.text().then((text) => {
    const isHtml = text.trimStart().startsWith('<')
    try {
      return JSON.parse(text)
    } catch (e) {
      // Сервер вернул HTML (страница ошибки) вместо JSON — не показываем сырой SyntaxError
      const msg =
        fallbackMessage ||
        (r.ok
          ? 'Ответ сервера в неверном формате'
          : `Сервер вернул ошибку (код ${r.status}). Проверьте логи backend: docker compose logs backend`)
      throw new Error(isHtml ? `Ошибка backend: ${msg}` : msg)
    }
  })
}

/** Загрузка .xlsx, парсинг и нечёткий поиск. */
export async function bulkUpload(file) {
  const form = new FormData()
  form.append('file', file)
  const r = await fetch(`${BASE}/api/bulk-upload/`, { method: 'POST', body: form })
  const data = await parseJsonOrThrow(
    r,
    'Ошибка при загрузке файла. Убедитесь, что в backend установлены pandas и rapidfuzz: docker compose build backend --no-cache && docker compose up -d backend'
  )
  if (!r.ok) throw new Error(data.error || 'Ошибка загрузки файла')
  return data
}

/** Массовое создание расчётов. rows: [{ matched_id, zone_id }] */
export async function confirmBulkCalculations(rows) {
  const r = await fetch(`${BASE}/api/calculations/bulk/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rows }),
  })
  const data = await parseJsonOrThrow(r)
  if (!r.ok) throw new Error(data.error || 'Ошибка создания расчётов')
  return data
}
