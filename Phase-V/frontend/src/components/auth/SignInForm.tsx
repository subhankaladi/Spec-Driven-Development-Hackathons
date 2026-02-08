// T025: SignInForm component with validation

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { validateEmail } from '@/lib/utils/validation';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { SignInFormState } from '@/types/auth';

interface SignInFormProps {
  onSuccess?: () => void;
  initialEmail?: string;
}

export function SignInForm({ onSuccess, initialEmail = '' }: SignInFormProps) {
  const { signIn } = useAuth();
  const [formState, setFormState] = useState<SignInFormState>({
    email: initialEmail,
    password: '',
    errors: {},
    touched: {
      email: false,
      password: false,
    },
    isSubmitting: false,
  });

  const handleBlur = (field: 'email' | 'password') => {
    setFormState((prev) => ({
      ...prev,
      touched: { ...prev.touched, [field]: true },
    }));
    validateField(field, formState[field]);
  };

  const validateField = (field: 'email' | 'password', value: string) => {
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
        delete errors.password;
      }
    }

    setFormState((prev) => ({ ...prev, errors }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setFormState((prev) => ({
      ...prev,
      touched: { email: true, password: true },
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
    }

    if (Object.keys(errors).length > 0) {
      setFormState((prev) => ({ ...prev, errors }));
      return;
    }

    try {
      setFormState((prev) => ({ ...prev, isSubmitting: true, errors: {} }));
      await signIn(formState.email, formState.password);
      onSuccess?.();
    } catch (error: any) {
      setFormState((prev) => ({
        ...prev,
        isSubmitting: false,
        errors: { general: error.message || 'Invalid credentials' },
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
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

      <Button
        type="submit"
        variant="primary"
        size="md"
        className="w-full"
        isLoading={formState.isSubmitting}
      >
        Sign In
      </Button>
    </form>
  );
}
