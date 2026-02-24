import { useState, useEffect } from 'react'
import { bulkUpload, getAllModels, getZones, confirmBulkCalculations } from '../api'
import BulkUploadTable from '../components/BulkUploadTable'
import './BulkUploadPage.css'

export default function BulkUploadPage() {
  const [rows, setRows] = useState([])
  const [zones, setZones] = useState([])
  const [models, setModels] = useState([])
  const [uploadLoading, setUploadLoading] = useState(false)
  const [confirmLoading, setConfirmLoading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [confirmError, setConfirmError] = useState(null)
  const [confirmSuccess, setConfirmSuccess] = useState(null)

  useEffect(() => {
    Promise.all([getZones(), getAllModels()])
      .then(([z, m]) => {
        setZones(z)
        setModels(m)
      })
      .catch(() => {})
  }, [])

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.name.endsWith('.xlsx')) {
      setUploadError('Нужен файл .xlsx')
      setRows([])
      return
    }
    setUploadError(null)
    setConfirmError(null)
    setConfirmSuccess(null)
    setUploadLoading(true)
    bulkUpload(file)
      .then((data) => setRows(data.rows || []))
      .catch((err) => {
        setUploadError(err.message)
        setRows([])
      })
      .finally(() => setUploadLoading(false))
    e.target.value = ''
  }

  const handleConfirm = (rowsToCreate) => {
    setConfirmError(null)
    setConfirmSuccess(null)
    setConfirmLoading(true)
    confirmBulkCalculations(rowsToCreate)
      .then((data) => {
        setConfirmSuccess(`Создано расчётов: ${data.count ?? data.created?.length ?? 0}`)
      })
      .catch((err) => setConfirmError(err.message))
      .finally(() => setConfirmLoading(false))
  }

  return (
    <div className="bulk-upload-page">
      <h2 className="bulk-upload-page__title">Пакетная загрузка</h2>
      <p className="bulk-upload-page__hint">
        Файл .xlsx с колонками «Техника» и «Зона защиты». После загрузки проверьте строки со статусом «Не найдено» и при необходимости выберите модель вручную.
      </p>
      <div className="bulk-upload-page__upload">
        <label className="bulk-upload-page__label">
          <span className="bulk-upload-page__label-text">Выберите файл</span>
          <input
            type="file"
            accept=".xlsx"
            onChange={handleFileChange}
            disabled={uploadLoading}
            className="bulk-upload-page__input"
          />
        </label>
        {uploadLoading && (
          <div className="bulk-upload-page__loading" aria-live="polite">
            Обработка файла…
          </div>
        )}
        {uploadError && (
          <div className="bulk-upload-page__error">{uploadError}</div>
        )}
      </div>
      {confirmSuccess && (
        <div className="bulk-upload-page__success">{confirmSuccess}</div>
      )}
      <BulkUploadTable
        rows={rows}
        onRowsChange={setRows}
        zones={zones}
        models={models}
        onConfirm={handleConfirm}
        confirmLoading={confirmLoading}
        confirmError={confirmError}
      />
    </div>
  )
}
