export const validateEmail = (email) => {
  if (!email) return 'Email is required';
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!re.test(email)) return 'Invalid email format';
  return null;
};

export const validatePassword = (password) => {
  if (!password) return 'Password is required';
  if (password.length < 6) return 'Password must be at least 6 characters';
  return null;
};

export const validateRequired = (value, fieldName) => {
  if (!value || (typeof value === 'string' && !value.trim())) {
    return `${fieldName} is required`;
  }
  return null;
};

export const validateThreshold = (value) => {
  if (value === '' || value == null) return 'Threshold is required';
  const num = Number(value);
  if (isNaN(num)) return 'Threshold must be a number';
  return null;
};

export const validateForm = (values, validators) => {
  const errors = {};
  for (const [field, validator] of Object.entries(validators)) {
    const error = validator(values[field]);
    if (error) errors[field] = error;
  }
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
