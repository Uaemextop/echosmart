import { Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Header from '../Common/Header';
import Sidebar from '../Common/Sidebar';

function DashboardLayout() {
  const { sidebarOpen } = useSelector((state) => state.ui);

  return (
    <>
      <Header />
      <div className="main-layout">
        <Sidebar />
        <main className={`main-content ${!sidebarOpen ? 'sidebar-closed' : ''}`}>
          <Outlet />
        </main>
      </div>
    </>
  );
}

export default DashboardLayout;
