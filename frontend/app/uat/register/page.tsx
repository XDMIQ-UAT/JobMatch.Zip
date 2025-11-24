'use client';

/**
 * UAT Tester Registration
 * 
 * Anonymous registration with cryptographic ID generation
 * Zero-knowledge proof for qualifications
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    experience: '',
    payment_method: 'usd_transfer',
    qualifications: [] as string[],
    agreed_to_terms: false
  });
  const [generatedId, setGeneratedId] = useState('');
  const [secret, setSecret] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (step === 1) {
      setStep(2);
      return;
    }

    // Call backend to generate anonymous ID
    try {
      const response = await fetch('/api/uat/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      setGeneratedId(data.tester_id);
      setSecret(data.secret);
      setStep(3);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  const downloadCredentials = () => {
    const credentials = {
      tester_id: generatedId,
      secret: secret,
      created_at: new Date().toISOString(),
      warning: 'KEEP THIS SECRET SAFE - Cannot be recovered if lost'
    };
    
    const blob = new Blob([JSON.stringify(credentials, null, 2)], 
      { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `uat-credentials-${generatedId.slice(0, 8)}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12">
      <div className="container mx-auto px-4 max-w-2xl">
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className={`text-sm ${step >= 1 ? 'text-purple-400' : 'text-gray-500'}`}>
              Qualifications
            </span>
            <span className={`text-sm ${step >= 2 ? 'text-purple-400' : 'text-gray-500'}`}>
              Payment
            </span>
            <span className={`text-sm ${step >= 3 ? 'text-purple-400' : 'text-gray-500'}`}>
              Complete
            </span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full">
            <div 
              className="h-full bg-purple-600 rounded-full transition-all"
              style={{ width: `${(step / 3) * 100}%` }}
            />
          </div>
        </div>

        {step === 1 && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
            <h1 className="text-3xl font-bold text-white mb-6">
              Register as Anonymous Tester
            </h1>

            <form onSubmit={handleSubmit}>
              {/* Experience Level */}
              <div className="mb-6">
                <label className="block text-purple-200 mb-2">
                  Testing Experience
                </label>
                <select
                  value={formData.experience}
                  onChange={(e) => setFormData({...formData, experience: e.target.value})}
                  className="w-full bg-white/5 border border-purple-500/30 rounded-lg px-4 py-3 text-white"
                  required
                >
                  <option value="">Select experience level</option>
                  <option value="beginner">Beginner (0-2 years)</option>
                  <option value="intermediate">Intermediate (3-5 years)</option>
                  <option value="advanced">Advanced (6-10 years)</option>
                  <option value="expert">Expert (10+ years)</option>
                </select>
              </div>

              {/* Qualifications */}
              <div className="mb-6">
                <label className="block text-purple-200 mb-2">
                  Areas of Expertise (select all that apply)
                </label>
                <div className="space-y-2">
                  {['Financial UI', 'Healthcare Systems', 'Legal Documents', 
                    'Payment Processing', 'Data Privacy', 'Accessibility'].map(qual => (
                    <label key={qual} className="flex items-center text-white">
                      <input
                        type="checkbox"
                        checked={formData.qualifications.includes(qual)}
                        onChange={(e) => {
                          const newQuals = e.target.checked
                            ? [...formData.qualifications, qual]
                            : formData.qualifications.filter(q => q !== qual);
                          setFormData({...formData, qualifications: newQuals});
                        }}
                        className="mr-2"
                      />
                      {qual}
                    </label>
                  ))}
                </div>
              </div>

              {/* Terms */}
              <div className="mb-6">
                <label className="flex items-start text-white">
                  <input
                    type="checkbox"
                    checked={formData.agreed_to_terms}
                    onChange={(e) => setFormData({...formData, agreed_to_terms: e.target.checked})}
                    className="mr-2 mt-1"
                    required
                  />
                  <span className="text-sm">
                    I understand that:
                    <ul className="list-disc ml-5 mt-2 text-purple-200">
                      <li>My identity will never be linked to test behavior</li>
                      <li>All test data is sanitized before display</li>
                      <li>Payment requires separate identity vault (optional)</li>
                      <li>I will receive a secret that cannot be recovered</li>
                    </ul>
                  </span>
                </label>
              </div>

              <button
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg transition"
              >
                Continue to Payment Setup
              </button>
            </form>
          </div>
        )}

        {step === 2 && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
            <h1 className="text-3xl font-bold text-white mb-6">
              Payment Setup
            </h1>

            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-purple-200 mb-2">
                  Preferred Payment Method
                </label>
                <select
                  value={formData.payment_method}
                  onChange={(e) => setFormData({...formData, payment_method: e.target.value})}
                  className="w-full bg-white/5 border border-purple-500/30 rounded-lg px-4 py-3 text-white"
                >
                  <option value="usd_transfer">USD Transfer (Wise/Stripe)</option>
                  <option value="bitcoin">Bitcoin</option>
                  <option value="crypto_general">Other Cryptocurrency</option>
                </select>
              </div>

              <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4 mb-6">
                <p className="text-yellow-200 text-sm">
                  <strong>Privacy Note:</strong> Payment information is stored in a 
                  separate identity vault and never linked to your test behavior. 
                  You can provide payment details later when requesting withdrawal.
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white font-bold py-3 rounded-lg transition"
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg transition"
                >
                  Generate Anonymous ID
                </button>
              </div>
            </form>
          </div>
        )}

        {step === 3 && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
            <h1 className="text-3xl font-bold text-white mb-6">
              ✅ Registration Complete
            </h1>

            <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-white mb-4">
                Your Anonymous Tester ID
              </h2>
              <div className="bg-black/30 rounded p-4 mb-4 font-mono text-sm text-green-300 break-all">
                {generatedId}
              </div>
              
              <h2 className="text-xl font-bold text-white mb-4">
                Your Secret Key
              </h2>
              <div className="bg-black/30 rounded p-4 mb-4 font-mono text-sm text-yellow-300 break-all">
                {secret}
              </div>

              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-4">
                <p className="text-red-200 text-sm font-bold">
                  ⚠️ CRITICAL: Save these credentials now!
                </p>
                <p className="text-red-200 text-sm mt-2">
                  This secret cannot be recovered. Without it, you cannot access 
                  your account or claim your earnings. Download the credentials 
                  file and store it securely.
                </p>
              </div>

              <button
                onClick={downloadCredentials}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition mb-4"
              >
                📥 Download Credentials File
              </button>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => router.push('/uat/scenarios')}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg transition"
              >
                Browse Available Tests
              </button>
              
              <button
                onClick={() => router.push('/uat')}
                className="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-3 rounded-lg transition"
              >
                Return to Portal
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
