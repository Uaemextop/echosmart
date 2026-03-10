import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { generateReport } from '../../store/reportsSlice';

function ReportGenerator() {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const { generating } = useSelector((state) => state.reports);

  const [formData, setFormData] = useState({
    title: '',
    format: 'pdf',
    from: '',
    to: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(generateReport(formData));
    setFormData({ title: '', format: 'pdf', from: '', to: '' });
  };

  return (
    <div className="card" style={{ marginBottom: '20px' }}>
      <h3 style={{ marginBottom: '16px' }}>{t('reports.generate')}</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>{t('reports.title')}</label>
          <input
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Report title"
            required
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label>{t('reports.format')}</label>
            <select name="format" value={formData.format} onChange={handleChange}>
              <option value="pdf">PDF</option>
              <option value="csv">CSV</option>
              <option value="xlsx">Excel</option>
            </select>
          </div>
          <div className="form-group">
            <label>From</label>
            <input type="date" name="from" value={formData.from} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>To</label>
            <input type="date" name="to" value={formData.to} onChange={handleChange} />
          </div>
        </div>
        <button className="btn btn-primary" type="submit" disabled={generating}>
          {generating ? t('common.loading') : t('reports.generate')}
        </button>
      </form>
    </div>
  );
}

export default ReportGenerator;
