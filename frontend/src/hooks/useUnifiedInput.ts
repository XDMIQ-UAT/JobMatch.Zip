import { useEffect, useRef, useCallback, useState } from 'react';

export interface UnifiedInputEvent {
  type: 'tap' | 'double-tap' | 'long-press' | 'swipe' | 'pinch' | 'drag' | 'hover' | 'pen';
  x: number;
  y: number;
  deltaX?: number;
  deltaY?: number;
  scale?: number;
  pressure?: number;
  tiltX?: number;
  tiltY?: number;
  timestamp: number;
  originalEvent: MouseEvent | TouchEvent | PointerEvent;
}

export interface UseUnifiedInputOptions {
  onTap?: (event: UnifiedInputEvent) => void;
  onDoubleTap?: (event: UnifiedInputEvent) => void;
  onLongPress?: (event: UnifiedInputEvent) => void;
  onSwipe?: (event: UnifiedInputEvent, direction: 'up' | 'down' | 'left' | 'right') => void;
  onPinch?: (event: UnifiedInputEvent) => void;
  onDrag?: (event: UnifiedInputEvent) => void;
  onHover?: (event: UnifiedInputEvent) => void;
  onPenInput?: (event: UnifiedInputEvent) => void;
  longPressDelay?: number;
  swipeThreshold?: number;
  doubleTapDelay?: number;
}

export function useUnifiedInput(
  elementRef: React.RefObject<HTMLElement>,
  options: UseUnifiedInputOptions = {}
) {
  const {
    onTap,
    onDoubleTap,
    onLongPress,
    onSwipe,
    onPinch,
    onDrag,
    onHover,
    onPenInput,
    longPressDelay = 500,
    swipeThreshold = 50,
    doubleTapDelay = 300,
  } = options;

  const [inputMode, setInputMode] = useState<'mouse' | 'touch' | 'pen'>('mouse');
  const lastTapRef = useRef<number>(0);
  const longPressTimerRef = useRef<NodeJS.Timeout | null>(null);
  const startPosRef = useRef<{ x: number; y: number } | null>(null);
  const isDraggingRef = useRef(false);
  const initialPinchDistanceRef = useRef<number | null>(null);

  const getEventCoordinates = useCallback((event: MouseEvent | TouchEvent | PointerEvent) => {
    if ('touches' in event && event.touches.length > 0) {
      return { x: event.touches[0].clientX, y: event.touches[0].clientY };
    } else if ('clientX' in event) {
      return { x: event.clientX, y: event.clientY };
    }
    return { x: 0, y: 0 };
  }, []);

  const createUnifiedEvent = useCallback((
    event: MouseEvent | TouchEvent | PointerEvent,
    type: UnifiedInputEvent['type'],
    additionalData: Partial<UnifiedInputEvent> = {}
  ): UnifiedInputEvent => {
    const coords = getEventCoordinates(event);
    const unifiedEvent: UnifiedInputEvent = {
      type,
      x: coords.x,
      y: coords.y,
      timestamp: Date.now(),
      originalEvent: event,
      ...additionalData,
    };

    // Add pen-specific data if available
    if ('pointerType' in event && event.pointerType === 'pen') {
      unifiedEvent.pressure = (event as PointerEvent).pressure;
      unifiedEvent.tiltX = (event as PointerEvent).tiltX;
      unifiedEvent.tiltY = (event as PointerEvent).tiltY;
      setInputMode('pen');
    }

    return unifiedEvent;
  }, [getEventCoordinates]);

  const handlePointerDown = useCallback((event: PointerEvent) => {
    const coords = getEventCoordinates(event);
    startPosRef.current = coords;
    isDraggingRef.current = false;

    // Detect input mode
    if (event.pointerType === 'pen') {
      setInputMode('pen');
      if (onPenInput) {
        const unifiedEvent = createUnifiedEvent(event, 'pen');
        onPenInput(unifiedEvent);
      }
    } else if (event.pointerType === 'touch') {
      setInputMode('touch');
    } else {
      setInputMode('mouse');
    }

    // Start long press timer
    longPressTimerRef.current = setTimeout(() => {
      if (onLongPress && startPosRef.current) {
        const unifiedEvent = createUnifiedEvent(event, 'long-press');
        onLongPress(unifiedEvent);
      }
    }, longPressDelay);

    // Check for double tap
    const now = Date.now();
    if (onDoubleTap && now - lastTapRef.current < doubleTapDelay) {
      const unifiedEvent = createUnifiedEvent(event, 'double-tap');
      onDoubleTap(unifiedEvent);
      lastTapRef.current = 0; // Reset to prevent triple tap
    } else {
      lastTapRef.current = now;
    }
  }, [getEventCoordinates, onLongPress, onDoubleTap, onPenInput, createUnifiedEvent, longPressDelay, doubleTapDelay]);

  const handlePointerMove = useCallback((event: PointerEvent) => {
    if (!startPosRef.current) return;

    const coords = getEventCoordinates(event);
    const deltaX = coords.x - startPosRef.current.x;
    const deltaY = coords.y - startPosRef.current.y;

    // Cancel long press if moved
    if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
        longPressTimerRef.current = null;
      }
    }

    // Detect drag
    if ((Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) && onDrag) {
      isDraggingRef.current = true;
      const unifiedEvent = createUnifiedEvent(event, 'drag', { deltaX, deltaY });
      onDrag(unifiedEvent);
    }

    // Hover for mouse
    if (event.pointerType === 'mouse' && onHover && !isDraggingRef.current) {
      const unifiedEvent = createUnifiedEvent(event, 'hover');
      onHover(unifiedEvent);
    }
  }, [getEventCoordinates, onDrag, onHover, createUnifiedEvent]);

  const handlePointerUp = useCallback((event: PointerEvent) => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }

    if (!startPosRef.current) return;

    const coords = getEventCoordinates(event);
    const deltaX = coords.x - startPosRef.current.x;
    const deltaY = coords.y - startPosRef.current.y;

    // Detect swipe
    if (onSwipe && (Math.abs(deltaX) > swipeThreshold || Math.abs(deltaY) > swipeThreshold)) {
      let direction: 'up' | 'down' | 'left' | 'right';
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        direction = deltaX > 0 ? 'right' : 'left';
      } else {
        direction = deltaY > 0 ? 'down' : 'up';
      }
      const unifiedEvent = createUnifiedEvent(event, 'swipe', { deltaX, deltaY });
      onSwipe(unifiedEvent, direction);
    }
    // Detect tap (if not dragging and not swiping)
    else if (onTap && !isDraggingRef.current && Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
      const unifiedEvent = createUnifiedEvent(event, 'tap');
      onTap(unifiedEvent);
    }

    startPosRef.current = null;
    isDraggingRef.current = false;
  }, [getEventCoordinates, onSwipe, onTap, createUnifiedEvent, swipeThreshold]);

  const handleTouchStart = useCallback((event: TouchEvent) => {
    if (event.touches.length === 2 && onPinch) {
      // Pinch gesture
      const touch1 = event.touches[0];
      const touch2 = event.touches[1];
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      initialPinchDistanceRef.current = distance;
    }
  }, [onPinch]);

  const handleTouchMove = useCallback((event: TouchEvent) => {
    if (event.touches.length === 2 && onPinch && initialPinchDistanceRef.current) {
      const touch1 = event.touches[0];
      const touch2 = event.touches[1];
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      const scale = distance / initialPinchDistanceRef.current;
      const centerX = (touch1.clientX + touch2.clientX) / 2;
      const centerY = (touch1.clientY + touch2.clientY) / 2;

      const unifiedEvent = createUnifiedEvent(event, 'pinch', {
        x: centerX,
        y: centerY,
        scale,
      });
      onPinch(unifiedEvent);
    }
  }, [onPinch, createUnifiedEvent]);

  const handleTouchEnd = useCallback(() => {
    initialPinchDistanceRef.current = null;
  }, []);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    // Add Pointer Events (unified for mouse, touch, pen)
    element.addEventListener('pointerdown', handlePointerDown as EventListener);
    element.addEventListener('pointermove', handlePointerMove as EventListener);
    element.addEventListener('pointerup', handlePointerUp as EventListener);

    // Add Touch Events for multi-touch gestures
    element.addEventListener('touchstart', handleTouchStart as EventListener);
    element.addEventListener('touchmove', handleTouchMove as EventListener);
    element.addEventListener('touchend', handleTouchEnd);

    return () => {
      element.removeEventListener('pointerdown', handlePointerDown as EventListener);
      element.removeEventListener('pointermove', handlePointerMove as EventListener);
      element.removeEventListener('pointerup', handlePointerUp as EventListener);
      element.removeEventListener('touchstart', handleTouchStart as EventListener);
      element.removeEventListener('touchmove', handleTouchMove as EventListener);
      element.removeEventListener('touchend', handleTouchEnd);

      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
      }
    };
  }, [
    elementRef,
    handlePointerDown,
    handlePointerMove,
    handlePointerUp,
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
  ]);

  return { inputMode };
}
