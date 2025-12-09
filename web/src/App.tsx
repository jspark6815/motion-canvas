import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Gallery from './pages/Gallery'
import Detail from './pages/Detail'
import Home from './pages/Home'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="gallery" element={<Gallery />} />
        <Route path="detail/:id" element={<Detail />} />
      </Route>
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />
    </Routes>
  )
}

export default App

