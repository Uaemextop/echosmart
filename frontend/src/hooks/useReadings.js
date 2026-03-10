import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchReadings } from '../store/readingsSlice';

export const useReadings = (sensorId, options = {}) => {
  const dispatch = useDispatch();
  const readings = useSelector(
    (state) => state.readings.data[sensorId] || []
  );
  const { loading, error } = useSelector((state) => state.readings);

  useEffect(() => {
    if (sensorId) {
      dispatch(
        fetchReadings({
          sensorId,
          from: options.from,
          to: options.to,
        })
      );
    }
  }, [dispatch, sensorId, options.from, options.to]);

  return { readings, loading, error };
};

export default useReadings;
