// T026: SignUpForm component with validation and confirm password

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { validateEmail, validatePassword } from '@/lib/utils/validation';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { SignUpFormState } from '@/types/auth';

interface SignUpFormProps {
  onSuccess?: () => void;
}

export function SignUpForm({ onSuccess }: SignUpFormProps) {
  const { signUp } = useAuth();
  const [formState, setFormState] = useState<SignUpFormState>({
    email: '',
    password: '',
    confirmPassword: '',
    errors: {},
    touched: {
      email: false,
      password: false,
      confirmPassword: false,
    },
    isSubmitting: false,
  });

  const handleBlur = (field: keyof typeof formState.touched) => {
    setFormState((prev) => ({
      ...prev,
      touched: { ...prev.touched, [field]: true },
    }));
    validateField(field, formState[field as keyof Pick<typeof formState, 'email' | 'password' | 'confirmPassword'>]);
  };

  const validateField = (
    field: keyof typeof formState.touched,
    value: string
  ) => {
    const errors = { ...formState.errors };

    if (field === 'email') {
      if (!value) {
        errors.email = 'Email is required';
      } else if (!validateEmail(value)) {
        errors.email = 'Invalid email format';
      } else {
        delete errors.email;
      }
    }

    if (field === 'password') {
      if (!value) {
        errors.password = 'Password is required';
      } else {
        const validation = validatePassword(value);
        if (!validation.valid) {
          errors.password = validation.errors[0];
        } else {
          delete errors.password;
        }
      }
    }

    if (field === 'confirmPassword') {
      if (!value) {
        errors.confirmPassword = 'Please confirm your password';
      } else if (value !== formState.password) {
        errors.confirmPassword = 'Passwords do not match';
      } else {
        delete errors.confirmPassword;
      }
    }

    setFormState((prev) => ({ ...prev, errors }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setFormState((prev) => ({
      ...prev,
      touched: { email: true, password: true, confirmPassword: true },
    }));

    // Validate all fields
    const errors: typeof formState.errors = {};

    if (!formState.email) {
      errors.email = 'Email is required';
    } else if (!validateEmail(formState.email)) {
      errors.email = 'Invalid email format';
    }

    if (!formState.password) {
      errors.password = 'Password is required';
    } else {
      const validation = validatePassword(formState.password);
      if (!validation.valid) {
        errors.password = validation.errors[0];
      }
    }

    if (!formState.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formState.confirmPassword !== formState.password) {
      errors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(errors).length > 0) {
      setFormState((prev) => ({ ...prev, errors }));
      return;
    }

    try {
      setFormState((prev) => ({ ...prev, isSubmitting: true, errors: {} }));
      await signUp(formState.email, formState.password);
      onSuccess?.();
    } catch (error: any) {
      setFormState((prev) => ({
        ...prev,
        isSubmitting: false,
        errors: { general: error.message || 'Sign up failed. Email may already exist.' },
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {formState.errors.general && (
        <div className="bg-danger-500/10 text-danger-400 border border-danger-500/20 p-3 rounded-xl text-sm" role="alert">
          {formState.errors.general}
        </div>
      )}

      <Input
        type="email"
        label="Email"
        value={formState.email}
        onChange={(e) =>
          setFormState((prev) => ({ ...prev, email: e.target.value }))
        }
        onBlur={() => handleBlur('email')}
        error={formState.errors.email}
        touched={formState.touched.email}
        required
        disabled={formState.isSubmitting}
      />

      <Input
        type="password"
        label="Password"
        value={formState.password}
        onChange={(e) =>
          setFormState((prev) => ({ ...prev, password: e.target.value }))
        }
        onBlur={() => handleBlur('password')}
        error={formState.errors.password}
        touched={formState.touched.password}
        required
        disabled={formState.isSubmitting}
      />

      <Input
        type="password"
        label="Confirm Password"
        value={formState.confirmPassword}
        onChange={(e) =>
          setFormState((prev) => ({ ...prev, confirmPassword: e.target.value }))
        }
        onBlur={() => handleBlur('confirmPassword')}
        error={formState.errors.confirmPassword}
        touched={formState.touched.confirmPassword}
        required
        disabled={formState.isSubmitting}
      />

      <Button
        type="submit"
        variant="primary"
        size="md"
        className="w-full"
        isLoading={formState.isSubmitting}
      >
        Sign Up
      </Button>
    </form>
  );
}
