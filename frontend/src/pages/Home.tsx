import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles, Shield, Zap, Target, Users, TrendingUp, CheckCircle2 } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4" />
              <span>AI-Powered Job Matching</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Find Your Perfect Match
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Built to Last
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              AI-powered job matching for LLC owners and independent contractors.
              <br />
              <span className="text-gray-500 text-lg">We prioritize long-term partnerships over quick placements.</span>
            </p>

            {/* Promotional Offer */}
            <div className="mb-8 inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl shadow-md">
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold text-green-600">$1</span>
                <span className="text-gray-600">for your first month</span>
              </div>
              <span className="text-gray-400">•</span>
              <span className="text-gray-600">Cancel anytime</span>
              <span className="text-gray-400">•</span>
              <span className="text-gray-600">Money-back guarantee</span>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link
                to="/assessment"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 flex items-center gap-2"
              >
                Sign Up Now - Just $1
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/matches"
                className="px-8 py-4 bg-white text-gray-900 rounded-xl font-semibold text-lg shadow-md hover:shadow-lg border-2 border-gray-200 hover:border-blue-300 transform hover:-translate-y-1 transition-all duration-200"
              >
                Try Demo First
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-green-500" />
                <span>Anonymous Identity</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-500" />
                <span>AI-Powered Matching</span>
              </div>
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-500" />
                <span>Capability-First</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Why JobMatch.zip?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Built for modern professionals who value privacy, capability, and long-term matches
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-6">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Zero-Knowledge Privacy</h3>
              <p className="text-gray-600 leading-relaxed">
                Your identity stays anonymous. We match based on capabilities, not credentials. 
                Your real identity is never revealed to employers.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mb-6">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">AI-Powered Matching</h3>
              <p className="text-gray-600 leading-relaxed">
                Advanced AI analyzes job descriptions and your profile to find matches that last. 
                We prioritize long-term compatibility over quick placements.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-pink-50 to-pink-100 border border-pink-200 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-pink-600 rounded-xl flex items-center justify-center mb-6">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Capability-First</h3>
              <p className="text-gray-600 leading-relaxed">
                Show what you can do, not just what credentials you have. 
                XDMIQ assessment reveals your true capabilities and preferences.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Simple, fast, and effective
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '1', title: 'Create Profile', desc: 'Build your anonymous profile with capabilities', icon: Users },
              { step: '2', title: 'Take Assessment', desc: 'Complete XDMIQ to reveal your preferences', icon: Target },
              { step: '3', title: 'AI Matching', desc: 'Our AI finds jobs that match your capabilities', icon: Sparkles },
              { step: '4', title: 'Long-Term Match', desc: 'Connect with employers for lasting partnerships', icon: TrendingUp },
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <item.icon className="w-8 h-8 text-white" />
                  </div>
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-2">
                    <span className="bg-gray-900 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                      {item.step}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
                {idx < 3 && (
                  <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 transform translate-x-4"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Benefits */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                Built for LLC Owners & Independent Contractors
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                We understand that traditional job boards don't work for modern professionals. 
                That's why we built JobMatch.zip differently.
              </p>
              <div className="space-y-4">
                {[
                  'Anonymous identity protection',
                  'Capability-based matching (not just credentials)',
                  'AI-powered bias detection and mitigation',
                  'Long-term match prioritization',
                  'XDMIQ preference assessment',
                  'Direct connection with hiring managers',
                ].map((benefit, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-lg text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl p-8 shadow-2xl">
                <div className="bg-white rounded-2xl p-8">
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Match Quality</span>
                      <span className="text-2xl font-bold text-gray-900">94%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full" style={{ width: '94%' }}></div>
                    </div>
                    <div className="pt-4 border-t border-gray-200">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-sm text-gray-500">Avg. Match Duration</div>
                          <div className="text-2xl font-bold text-gray-900">18+ months</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-500">Success Rate</div>
                          <div className="text-2xl font-bold text-gray-900">87%</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="mb-6 inline-flex items-center gap-3 px-6 py-3 bg-white/20 backdrop-blur-sm border-2 border-white/30 rounded-xl">
            <span className="text-2xl font-bold text-white">$1</span>
            <span className="text-blue-100">for your first month</span>
            <span className="text-white/50">•</span>
            <span className="text-blue-100">Cancel anytime</span>
            <span className="text-white/50">•</span>
            <span className="text-blue-100">100% money-back guarantee</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Find Your Perfect Match?
          </h2>
          <p className="text-xl text-blue-100 mb-10">
            Join thousands of professionals who've found lasting partnerships through JobMatch.zip
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/assessment"
              className="px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 flex items-center justify-center gap-2"
            >
              Sign Up Now - Just $1
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/matches"
              className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-xl font-semibold text-lg hover:bg-white hover:text-blue-600 transform hover:-translate-y-1 transition-all duration-200"
            >
              Try Demo First
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-bold text-lg mb-4">JobMatch.zip</h3>
              <p className="text-sm">
                AI-powered job matching for modern professionals.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/matches" className="hover:text-white">Browse Matches</Link></li>
                <li><Link to="/assessment" className="hover:text-white">Assessment</Link></li>
                <li><Link to="/matching" className="hover:text-white">Matching</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-sm">
                <li>Anonymous Identity</li>
                <li>AI Matching</li>
                <li>Bias Detection</li>
                <li>XDMIQ Assessment</li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/privacy" className="hover:text-white">Privacy</Link></li>
                <li><Link to="/terms" className="hover:text-white">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; 2025 JobMatch.zip. All rights reserved.</p>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}
