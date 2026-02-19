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
