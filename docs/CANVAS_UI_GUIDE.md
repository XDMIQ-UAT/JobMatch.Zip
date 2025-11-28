# Canvas-Based UI for Non-Keyboard Users - Implementation Guide

## Overview
The JobMatch UI has been remodeled to support users who cannot use keyboards, providing accessible canvas-based interactions for mouse, pen/stylus, and touch input.

## Features Implemented

### 1. Unified Input System (`useUnifiedInput` hook)
**Location:** `frontend/src/hooks/useUnifiedInput.ts`

A custom React hook that normalizes all input types (mouse, touch, pen) into a single interface.

**Supported Gestures:**
- **Tap** - Single quick touch/click
- **Double Tap** - Two quick taps in succession
- **Long Press** - Hold for 500ms (configurable)
- **Swipe** - Quick directional gesture (up/down/left/right)
- **Pinch** - Two-finger zoom gesture
- **Drag** - Touch and move
- **Hover** - Mouse-only hover detection
- **Pen Input** - Pressure-sensitive stylus input with tilt detection

**Usage Example:**
```typescript
import { useUnifiedInput } from '@/hooks/useUnifiedInput';

const MyComponent = () => {
  const elementRef = useRef<HTMLDivElement>(null);
  
  const { inputMode } = useUnifiedInput(elementRef, {
    onTap: (event) => console.log('Tapped at', event.x, event.y),
    onSwipe: (event, direction) => console.log('Swiped', direction),
    onLongPress: (event) => console.log('Long press detected'),
    onPinch: (event) => console.log('Pinch zoom', event.scale),
    longPressDelay: 500,
    swipeThreshold: 50,
  });
  
  return <div ref={elementRef}>Interactive content</div>;
};
```

### 2. Swipe Cards Component
**Location:** `frontend/src/components/SwipeCards.tsx`

A Tinder-style swipeable card interface for browsing job opportunities.

**Features:**
- Swipe left to pass, right to save
- Tap card for details
- Large touch targets (80x80px minimum for buttons)
- Visual feedback during drag
- Progress indicator
- Snap-back animation if swipe is incomplete
- Manual control buttons as alternative to swiping

**Integration:**
```typescript
import { SwipeCards } from '@/components';

<SwipeCards
  cards={jobCards}
  onSwipeLeft={(card) => handlePass(card)}
  onSwipeRight={(card) => handleSave(card)}
  onCardTap={(card) => showDetails(card)}
/>
```

**Accessible via:** `/matches` page with "Swipe View" toggle

### 3. Skill Bubbles Component
**Location:** `frontend/src/components/SkillBubbles.tsx`

Visual drag-and-drop interface for skill selection.

**Features:**
- Drag skills from categories into selection zone
- Tap to toggle skills on/off
- Skills organized by category (Programming Languages, Frameworks, etc.)
- Large touch targets (minimum 56x56px with padding)
- Visual drop zone with active state feedback
- Sticky progress bar at bottom
- Works in both canvas and list modes

**Integration:**
```typescript
import { SkillBubbles } from '@/components';

<SkillBubbles
  availableSkills={skillOptions}
  selectedSkills={selected}
  onSkillsChange={(skills) => setSelected(skills)}
  canvasMode={true}
/>
```

**Accessible via:** `/assess` page skills selection step

### 4. Radial Menu Component
**Location:** `frontend/src/components/RadialMenu.tsx`

Context menu triggered by long-press for touch-friendly navigation.

**Features:**
- Circular menu layout around center point
- Long-press to activate
- Up to 8 items arranged radially
- Large touch targets (80x80px per item)
- Visual connection lines to center
- Click outside or center to close
- Customizable colors and icons per item

**Usage Example:**
```typescript
import { RadialMenu } from '@/components';

const menuItems = [
  { id: '1', icon: '📝', label: 'Edit', action: () => handleEdit() },
  { id: '2', icon: '🗑️', label: 'Delete', action: () => handleDelete() },
  { id: '3', icon: '📤', label: 'Share', action: () => handleShare() },
  { id: '4', icon: '⭐', label: 'Favorite', action: () => handleFavorite() },
];

<RadialMenu
  items={menuItems}
  trigger={<button>Long press me</button>}
  onOpen={() => console.log('Menu opened')}
/>
```

### 5. Enhanced Matches Page
**Location:** `frontend/src/app/matches/page.tsx`

**New Features:**
- Toggle between List View and Swipe View
- Swipe View uses SwipeCards component
- Saved/passed state tracking
- Automatic filtering of reviewed cards in swipe mode

### 6. Enhanced Assess Page
**Location:** `frontend/src/app/assess/page.tsx`

**New Features:**
- Toggle between Canvas Mode and List Mode for skill selection
- Canvas Mode uses SkillBubbles component with drag-and-drop
- Skills organized by category
- Quest 3 VR optimizations

## Touch Target Guidelines

All interactive elements follow accessibility best practices:

- **Minimum touch target:** 44x44px (WCAG 2.1 AAA)
- **Implemented touch targets:**
  - Buttons: 80x80px (large), 56x56px (medium)
  - Skill bubbles: 120x56px minimum
  - Swipe cards: Full card is draggable
  - Radial menu items: 80x80px

## Input Mode Detection

The system automatically detects and adapts to:

1. **Mouse** - Traditional desktop interaction
2. **Touch** - Mobile/tablet touchscreen
3. **Pen** - Stylus input (e.g., Apple Pencil, Surface Pen)
   - Pressure sensitivity captured
   - Tilt angle captured
   - Barrel button support

Current input mode is displayed in UI with indicator badges:
- 🖱️ Mouse
- 👆 Touch  
- ✏️ Pen

## VR/Quest 3 Optimizations

The UI has been optimized for Meta Quest 3:

- **Extra-large text** - Minimum 2xl (24px) for body text
- **Large spacing** - Generous padding and gaps
- **High contrast** - Clear visual hierarchy
- **VR mode indicator** - "🥽 Quest 3 Optimized" badge
- **Controller-friendly** - Large hit targets for ray casting

## Browser Compatibility

**Fully Supported:**
- Chrome/Edge 89+ (Pointer Events API)
- Firefox 87+
- Safari 13+ (iOS and macOS)
- Mobile browsers (iOS Safari, Chrome Mobile)

**Gesture Support:**
- **Desktop:** Mouse, pen/stylus via Pointer Events
- **Mobile:** Touch events, multi-touch gestures
- **Tablet:** Touch + pen hybrid mode

## Performance Optimizations

- Pointer Events used over separate mouse/touch handlers
- Debounced drag events
- RequestAnimationFrame for smooth animations
- Touch-action CSS to prevent default behaviors
- Lazy component rendering

## Remaining Enhancements (Future)

The following items from the original roadmap are marked for future implementation:

1. **Virtual Keyboard** - On-screen keyboard for text input
2. **Handwriting Recognition** - Convert stylus writing to text
3. **Accessibility Enhancements:**
   - High contrast mode toggle
   - UI scaling (150%, 200%, 250%)
   - Haptic feedback for touch devices
4. **Enhanced CanvasFormField** - Full gesture integration

## Testing Recommendations

### Manual Testing Checklist

**Mouse Users:**
- [ ] Can click all buttons and cards
- [ ] Hover states work correctly
- [ ] Drag-and-drop skills functions
- [ ] Radial menu triggers on long click

**Touch Users (Mobile/Tablet):**
- [ ] All buttons respond to tap
- [ ] Swipe gestures work smoothly
- [ ] Pinch-to-zoom works (where applicable)
- [ ] Long-press triggers radial menu
- [ ] No accidental taps during scrolling

**Pen/Stylus Users:**
- [ ] Drawing/writing is smooth
- [ ] Pressure sensitivity captured
- [ ] Tilt angle affects input (if implemented)
- [ ] Palm rejection works

**VR Users (Quest 3):**
- [ ] Text is readable at distance
- [ ] Ray-cast selection works on all buttons
- [ ] Hand tracking responds to gestures
- [ ] No UI elements too small to hit

## File Structure

```
frontend/src/
├── hooks/
│   └── useUnifiedInput.ts          # Unified input abstraction
├── components/
│   ├── SwipeCards.tsx              # Swipeable job cards
│   ├── SkillBubbles.tsx            # Drag-drop skill selection
│   ├── RadialMenu.tsx              # Long-press context menu
│   ├── CanvasFormField.tsx         # Existing canvas component
│   └── index.ts                    # Component exports
├── app/
│   ├── assess/page.tsx             # Enhanced with canvas mode
│   ├── matches/page.tsx            # Enhanced with swipe view
│   └── page.tsx                    # Landing page (VR-optimized)
```

## Dependencies Added

```json
{
  "fabric": "^5.3.0",           // Canvas object management
  "hammerjs": "^2.0.8",         // Gesture recognition
  "react-signature-canvas": "^1.0.6",  // Signature/drawing
  "perfect-freehand": "^1.2.0"  // Smooth drawing paths
}
```

## Development Commands

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Type checking
npm run typecheck

# Linting
npm run lint
```

## Future Enhancements

### Phase 2 (Priority)
- Virtual on-screen keyboard
- Handwriting-to-text conversion
- Voice input integration

### Phase 3 (Accessibility)
- High contrast theme toggle
- Configurable UI scaling
- Haptic feedback API integration
- Screen reader announcements for gestures

### Phase 4 (Advanced)
- Custom gesture creation
- Multi-user collaborative canvas
- Offline gesture sync
- AI-assisted input prediction

## Support & Feedback

For issues or feature requests related to canvas/touch interactions:
1. Check the troubleshooting section below
2. Test on multiple devices/input methods
3. Document the specific input mode and gesture that failed
4. Include browser version and device info

## Troubleshooting

### Gestures Not Working
- Ensure browser supports Pointer Events API
- Check that touch-action CSS is not blocking gestures
- Verify element has proper ref attached
- Check console for JavaScript errors

### Poor Performance
- Reduce number of simultaneous animated elements
- Check for memory leaks in event listeners
- Use Chrome DevTools Performance tab
- Enable hardware acceleration

### Incorrect Touch Targets
- Inspect element size in DevTools
- Verify min-width/height CSS properties
- Check for overlapping elements
- Test with touch visualizer tools

## Contributing

When adding new touch/gesture interactions:
1. Use `useUnifiedInput` hook for consistency
2. Ensure minimum 44x44px touch targets
3. Provide visual feedback for all interactions
4. Test on mouse, touch, and pen inputs
5. Add appropriate ARIA labels
6. Document gesture requirements

---

**Last Updated:** November 24, 2025  
**Version:** 1.0.0  
**Maintainer:** JobMatch Development Team
