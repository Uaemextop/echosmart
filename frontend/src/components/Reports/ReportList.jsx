import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { fetchReports } from '../../store/reportsSlice';
import { formatDate } from '../../utils/format';
import ReportGenerator from './ReportGenerator';
import LoadingSpinner from '../Common/LoadingSpinner';

function ReportList() {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const { items, error } = useSelector((state) => state.reports);

  useEffect(() => {
    dispatch(fetchReports());
  }, [dispatch]);

  if (error) return <div className="error-message">{error}</div>;

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>{t('reports.title')}</h2>
      <ReportGenerator />

      <div className="card table-container">
        <table>
          <thead>
            <tr>
              <th>{t('reports.title')}</th>
              <th>{t('reports.format')}</th>
              <th>{t('reports.status')}</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {items.map((report) => (
              <tr key={report.id}>
                <td style={{ fontWeight: 500 }}>{report.title}</td>
                <td>{report.format?.toUpperCase()}</td>
                <td>
                  <span className={`badge ${report.status === 'completed' ? 'badge-online' : 'badge-medium'}`}>
                    {report.status}
                  </span>
                </td>
                <td>{formatDate(report.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && (
          <p style={{ textAlign: 'center', color: '#64748b', padding: '40px' }}>
            No reports generated yet
          </p>
        )}
      </div>
    </div>
  );
}

export default ReportList;
