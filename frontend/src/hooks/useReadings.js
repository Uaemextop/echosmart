import { useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchReadings } from '../store/readingsSlice';

export const useReadings = (sensorId, options = {}) => {
  const dispatch = useDispatch();
  const readings = useSelector(
    (state) => state.readings.data[sensorId] || []
  );
  const { loading, error } = useSelector((state) => state.readings);

  const from = options.from;
  const to = options.to;

  const params = useMemo(() => ({ sensorId, from, to }), [sensorId, from, to]);

  useEffect(() => {
    if (params.sensorId) {
      dispatch(fetchReadings(params));
    }
  }, [dispatch, params]);

  return { readings, loading, error };
};

export default useReadings;
