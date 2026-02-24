import ConstructorPage from './pages/ConstructorPage'
import BulkUploadPage from './pages/BulkUploadPage'

function App() {
  return (
    <div>
      <ConstructorPage />
      <hr style={{ margin: '2rem 0', border: 'none', borderTop: '1px solid #ddd' }} />
      <BulkUploadPage />
    </div>
  )
}

export default App
