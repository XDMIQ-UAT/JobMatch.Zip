'use client'

import { useEffect, useState } from 'react'
import { fetchUserLocale } from '@/lib/apiCache'

interface RotatingHeroProps {
  locale?: string
  anonymousId?: string
}

// Hero text translations
const heroTexts: Record<string, string[]> = {
  'en': [
    'AI-Enabled LLC Matching Platform',
    'Match Your AI Skills with Opportunities',
    'Capability Over Credentials',
    'Find Your Perfect AI Job Match',
    'Anonymous. Secure. Powerful.'
  ],
  'es': [
    'Plataforma de Emparejamiento LLC Habilitada por IA',
    'Empareja Tus Habilidades de IA con Oportunidades',
    'Capacidad Sobre Credenciales',
    'Encuentra Tu Emparejamiento de Trabajo de IA Perfecto',
    'Anónimo. Seguro. Poderoso.'
  ],
  'fr': [
    'Plateforme de Correspondance LLC Alimentée par IA',
    'Associez Vos Compétences en IA aux Opportunités',
    'Capacité au Lieu de Crédentials',
    'Trouvez Votre Correspondance de Travail IA Parfaite',
    'Anonyme. Sécurisé. Puissant.'
  ],
  'de': [
    'KI-gestützte LLC-Matching-Plattform',
    'Passen Sie Ihre KI-Fähigkeiten an Möglichkeiten an',
    'Fähigkeit Statt Qualifikationen',
    'Finden Sie Ihre Perfekte KI-Jobübereinstimmung',
    'Anonym. Sicher. Leistungsstark.'
  ],
  'zh': [
    'AI驱动的LLC匹配平台',
    '将您的AI技能与机会匹配',
    '能力胜过证书',
    '找到您完美的AI工作匹配',
    '匿名。安全。强大。'
  ],
  'ja': [
    'AI対応LLCマッチングプラットフォーム',
    'AIスキルを機会とマッチング',
    '資格よりも能力',
    '完璧なAIジョブマッチを見つける',
    '匿名。安全。強力。'
  ],
  'pt': [
    'Plataforma de Correspondência LLC Habilitada por IA',
    'Combine Suas Habilidades de IA com Oportunidades',
    'Capacidade em Vez de Credenciais',
    'Encontre Sua Correspondência de Trabalho de IA Perfeita',
    'Anônimo. Seguro. Poderoso.'
  ],
  'ru': [
    'Платформа для подбора LLC с поддержкой ИИ',
    'Сопоставьте свои навыки ИИ с возможностями',
    'Способности важнее дипломов',
    'Найдите идеальное соответствие работы с ИИ',
    'Анонимно. Безопасно. Мощно.'
  ],
  'ar': [
    'منصة مطابقة LLC المدعومة بالذكاء الاصطناعي',
    'طابق مهاراتك في الذكاء الاصطناعي مع الفرص',
    'القدرة على الشهادات',
    'ابحث عن تطابق وظيفة الذكاء الاصطناعي المثالي',
    'مجهول. آمن. قوي.'
  ],
  'hi': [
    'AI-सक्षम LLC मिलान प्लेटफॉर्म',
    'अवसरों के साथ अपने AI कौशल का मिलान करें',
    'क्रेडेंशियल्स पर क्षमता',
    'अपना सही AI नौकरी मिलान खोजें',
    'अज्ञात। सुरक्षित। शक्तिशाली।'
  ]
}

// Default fallback to English
const defaultLocale = 'en'
const defaultTexts = heroTexts[defaultLocale]

export default function RotatingHero({ locale, anonymousId }: RotatingHeroProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [userLocale, setUserLocale] = useState<string>(locale || defaultLocale)

  // Fetch user locale from API if anonymousId is provided
  useEffect(() => {
    if (locale) {
      // Use provided locale
      setUserLocale(heroTexts[locale] ? locale : defaultLocale)
    } else if (anonymousId) {
      // Fetch from API using cached utility
      fetchUserLocale(anonymousId)
        .then(preferredLanguage => {
          if (preferredLanguage && heroTexts[preferredLanguage]) {
            setUserLocale(preferredLanguage)
          } else {
            // Fallback to browser locale
            const browserLocale = navigator.language.split('-')[0]
            setUserLocale(heroTexts[browserLocale] ? browserLocale : defaultLocale)
          }
        })
        .catch(() => {
          // Fallback to browser locale
          const browserLocale = navigator.language.split('-')[0]
          setUserLocale(heroTexts[browserLocale] ? browserLocale : defaultLocale)
        })
    } else {
      // Use browser locale as fallback
      const browserLocale = navigator.language.split('-')[0]
      setUserLocale(heroTexts[browserLocale] ? browserLocale : defaultLocale)
    }
  }, [anonymousId, locale])

  // Get texts for current locale
  const texts = heroTexts[userLocale] || defaultTexts

  // Rotate through texts
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % texts.length)
    }, 3000) // Change every 3 seconds

    return () => clearInterval(interval)
  }, [texts.length])

  return (
    <h1 
      className="text-4xl" 
      style={{ 
        marginBottom: 'var(--spacing-md)', 
        marginTop: 0,
        minHeight: '3rem',
        transition: 'opacity 0.5s ease-in-out'
      }}
      key={currentIndex} // Force re-render for animation
    >
      {texts[currentIndex]}
    </h1>
  )
}

