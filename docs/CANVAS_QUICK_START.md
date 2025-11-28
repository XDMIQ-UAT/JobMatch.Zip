# Canvas UI - Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
cd E:\zip-jobmatch\frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 3. Test New Features

#### A. Swipe Cards (Job Browsing)
1. Navigate to `/matches` page
2. Click "👆 Swipe View" button
3. **Try these interactions:**
   - 🖱️ **Mouse:** Click and drag cards left/right
   - 👆 **Touch:** Swipe cards with your finger
   - ✏️ **Pen:** Drag with stylus
   - **Buttons:** Use large ✕ / ℹ️ / ✓ buttons at bottom

#### B. Skill Bubbles (Drag & Drop)
1. Navigate to `/assess` page
2. Click "Let's start" → Continue to skills step
3. Ensure "Canvas Mode" is active (toggle if needed)
4. **Try these interactions:**
   - 🖱️ **Mouse:** Drag skill bubbles to drop zone
   - 👆 **Touch:** Tap skills or drag to drop zone
   - ✏️ **Pen:** Drag with stylus
   - **Alternative:** Tap any skill to toggle selection

#### C. Input Mode Detection
Watch for the badge in the top-right showing current input mode:
- 🖱️ Mouse
- 👆 Touch
- ✏️ Pen

The UI automatically adapts to your input device!

#### D. Radial Menu (Advanced)
Long-press any trigger element to open a circular context menu:
- **Desktop:** Long-click (hold 500ms)
- **Touch:** Long-press with finger
- **Pen:** Long-press with stylus

*Note: RadialMenu is available as a component but not yet integrated into main flows*

## Testing on Different Devices

### Desktop Computer (Mouse)
✅ All features work  
✅ Hover states visible  
✅ Click and drag smooth  

### Tablet (Touch)
✅ All features work  
✅ Swipe gestures responsive  
✅ No accidental clicks  
✅ Large touch targets easy to hit  

### Tablet + Stylus (Pen)
✅ All features work  
✅ Pressure sensitivity captured  
✅ Drawing smooth  
✅ Palm rejection (if hardware supports)  

### VR Headset (Quest 3)
✅ All features work  
✅ Extra-large text readable  
✅ Ray-cast pointer works  
✅ Hand tracking supported  
🥽 "Quest 3 Optimized" badge shows  

## Component Examples

### Using SwipeCards
```typescript
import { SwipeCards } from '@/components';

const cards = [
  {
    id: '1',
    title: 'Senior Developer',
    company: 'TechCorp',
    description: 'Build amazing apps',
    skills: ['React', 'TypeScript'],
    matchScore: 95,
    location: 'Remote',
    remote: true,
  },
];

<SwipeCards
  cards={cards}
  onSwipeLeft={(card) => console.log('Pass:', card.title)}
  onSwipeRight={(card) => console.log('Save:', card.title)}
  onCardTap={(card) => console.log('Details:', card.title)}
/>
```

### Using SkillBubbles
```typescript
import { SkillBubbles } from '@/components';

const skills = [
  { id: '1', name: 'Python', category: 'Languages' },
  { id: '2', name: 'React', category: 'Frameworks' },
];

<SkillBubbles
  availableSkills={skills}
  selectedSkills={[]}
  onSkillsChange={(selected) => console.log(selected)}
  canvasMode={true}
/>
```

### Using RadialMenu
```typescript
import { RadialMenu } from '@/components';

const actions = [
  { id: '1', icon: '📝', label: 'Edit', action: () => alert('Edit') },
  { id: '2', icon: '🗑️', label: 'Delete', action: () => alert('Delete') },
];

<RadialMenu
  items={actions}
  trigger={<button className="px-6 py-3">Long press me</button>}
/>
```

### Using useUnifiedInput Hook
```typescript
import { useRef } from 'react';
import { useUnifiedInput } from '@/hooks/useUnifiedInput';

function MyComponent() {
  const elementRef = useRef<HTMLDivElement>(null);
  
  const { inputMode } = useUnifiedInput(elementRef, {
    onTap: (e) => console.log('Tap at', e.x, e.y),
    onSwipe: (e, dir) => console.log('Swipe', dir),
    onLongPress: (e) => console.log('Long press'),
    onPinch: (e) => console.log('Pinch zoom', e.scale),
  });
  
  return (
    <div ref={elementRef}>
      <p>Current mode: {inputMode}</p>
      <p>Interact with me!</p>
    </div>
  );
}
```

## Keyboard Shortcuts (For Developers)

While the UI is designed for non-keyboard users, developers can use:

- **Ctrl+Shift+C** - Open browser DevTools
- **F12** - Open browser DevTools
- **Ctrl+Shift+M** - Toggle mobile view (Chrome)
- **Ctrl+Shift+I** - Open Inspector

## Common Issues & Solutions

### Issue: Gestures not responding
**Solution:** Check browser console for errors. Ensure ref is attached to element.

### Issue: Touch targets too small
**Solution:** All interactive elements should be minimum 44x44px. Check CSS.

### Issue: Swipe cards stuck
**Solution:** Refresh page. Check that `isAnimating` state resets properly.

### Issue: Input mode not detected
**Solution:** The Pointer Events API detects input automatically. Check browser compatibility.

## Browser Testing Matrix

| Feature | Chrome | Firefox | Safari | Mobile Safari | Edge |
|---------|--------|---------|--------|---------------|------|
| Mouse input | ✅ | ✅ | ✅ | N/A | ✅ |
| Touch input | ✅ | ✅ | ✅ | ✅ | ✅ |
| Pen input | ✅ | ✅ | ✅ | ✅ (iPad) | ✅ |
| Gestures | ✅ | ✅ | ✅ | ✅ | ✅ |
| Pinch zoom | ✅ | ✅ | ✅ | ✅ | ✅ |

## Next Steps

1. ✅ Test all interactions with your preferred input device
2. ✅ Try switching between input modes (mouse → touch → pen)
3. ✅ Test on mobile device or tablet if available
4. ✅ Try VR mode if you have a Quest 3
5. 📝 Report any issues or suggestions

## Performance Tips

- **Reduce animations** if performance is poor
- **Use hardware acceleration** in browser settings
- **Close other tabs** to free up memory
- **Update graphics drivers** for best performance

## Feedback

Found a bug or have a suggestion?
1. Note which input mode you were using
2. Describe the expected vs actual behavior
3. Include browser and device info
4. Check console for errors

## Resources

- [Full Documentation](./CANVAS_UI_GUIDE.md)
- [Original Roadmap](../plans/) 
- [Component Examples](./examples/)

---

**Happy Testing! 🎉**

Try all the gestures and see how the UI adapts to your input method. The future of accessible job matching starts here!
