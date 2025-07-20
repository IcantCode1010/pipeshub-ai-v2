const defaultOptions = {
  direction: 'forward',
  speed: 2,
  startDelay: 1000,
  active: true,
  breakpoints: {},
  playOnInit: true,
  stopOnFocusIn: true,
  stopOnInteraction: true,
  stopOnMouseEnter: false,
  rootNode: null
};

function AutoScroll(userOptions = {}) {
  let options;
  let emblaApi;
  let destroyed;
  let playing = false;
  let resume = true;
  let timer = 0;
  let startDelay;
  let defaultScrollBehaviour;
  function init(emblaApiInstance, optionsHandler) {
    emblaApi = emblaApiInstance;
    const {
      mergeOptions,
      optionsAtMedia
    } = optionsHandler;
    const optionsBase = mergeOptions(defaultOptions, AutoScroll.globalOptions);
    const allOptions = mergeOptions(optionsBase, userOptions);
    options = optionsAtMedia(allOptions);
    if (emblaApi.scrollSnapList().length <= 1) return;
    startDelay = options.startDelay;
    destroyed = false;
    defaultScrollBehaviour = emblaApi.internalEngine().scrollBody;
    const {
      eventStore
    } = emblaApi.internalEngine();
    const emblaRoot = emblaApi.rootNode();
    const root = options.rootNode && options.rootNode(emblaRoot) || emblaRoot;
    const container = emblaApi.containerNode();
    emblaApi.on('pointerDown', stopScroll);
    if (!options.stopOnInteraction) {
      emblaApi.on('pointerUp', startScrollOnSettle);
    }
    if (options.stopOnMouseEnter) {
      eventStore.add(root, 'mouseenter', () => {
        resume = false;
        stopScroll();
      });
      if (!options.stopOnInteraction) {
        eventStore.add(root, 'mouseleave', () => {
          resume = true;
          startScroll();
        });
      }
    }
    if (options.stopOnFocusIn) {
      emblaApi.on('slideFocusStart', stopScroll);
      if (!options.stopOnInteraction) {
        eventStore.add(container, 'focusout', startScroll);
      }
    }
    if (options.playOnInit) startScroll();
  }
  function destroy() {
    emblaApi.off('pointerDown', stopScroll).off('pointerUp', startScrollOnSettle).off('slideFocusStart', stopScroll).off('settle', onSettle);
    stopScroll();
    destroyed = true;
    playing = false;
  }
  function startScroll() {
    if (destroyed || playing) return;
    if (!resume) return;
    emblaApi.emit('autoScroll:play');
    const engine = emblaApi.internalEngine();
    const {
      ownerWindow
    } = engine;
    timer = ownerWindow.setTimeout(() => {
      engine.scrollBody = createAutoScrollBehaviour(engine);
      engine.animation.start();
    }, startDelay);
    playing = true;
  }
  function stopScroll() {
    if (destroyed || !playing) return;
    emblaApi.emit('autoScroll:stop');
    const engine = emblaApi.internalEngine();
    const {
      ownerWindow
    } = engine;
    engine.scrollBody = defaultScrollBehaviour;
    ownerWindow.clearTimeout(timer);
    timer = 0;
    playing = false;
  }
  function onSettle() {
    if (resume) startScroll();
    emblaApi.off('settle', onSettle);
  }
  function startScrollOnSettle() {
    emblaApi.on('settle', onSettle);
  }
  function createAutoScrollBehaviour(engine) {
    const {
      location,
      previousLocation,
      offsetLocation,
      target,
      scrollTarget,
      index,
      indexPrevious,
      limit: {
        reachedMin,
        reachedMax,
        constrain
      },
      options: {
        loop
      }
    } = engine;
    const directionSign = options.direction === 'forward' ? -1 : 1;
    const noop = () => self;
    let bodyVelocity = 0;
    let scrollDirection = 0;
    let rawLocation = location.get();
    let rawLocationPrevious = 0;
    let hasSettled = false;
    function seek(timeStep) {
      const fixedDeltaTimeSeconds = timeStep / 1000;
      let directionDiff = 0;
      previousLocation.set(location);
      bodyVelocity = directionSign * options.speed * 55;
      rawLocation += bodyVelocity;
      location.add(bodyVelocity * fixedDeltaTimeSeconds);
      target.set(location);
      directionDiff = rawLocation - rawLocationPrevious;
      scrollDirection = Math.sign(directionDiff);
      rawLocationPrevious = rawLocation;
      const currentIndex = scrollTarget.byDistance(0, false).index;
      if (index.get() !== currentIndex) {
        indexPrevious.set(index.get());
        index.set(currentIndex);
        emblaApi.emit('select');
      }
      const reachedEnd = options.direction === 'forward' ? reachedMin(offsetLocation.get()) : reachedMax(offsetLocation.get());
      if (!loop && reachedEnd) {
        hasSettled = true;
        const constrainedLocation = constrain(location.get());
        location.set(constrainedLocation);
        target.set(location);
        stopScroll();
      }
      return self;
    }
    const self = {
      direction: () => scrollDirection,
      duration: () => -1,
      velocity: () => bodyVelocity,
      settled: () => hasSettled,
      seek,
      useBaseFriction: noop,
      useBaseDuration: noop,
      useFriction: noop,
      useDuration: noop
    };
    return self;
  }
  function play(startDelayOverride) {
    if (typeof startDelayOverride !== 'undefined') {
      startDelay = startDelayOverride;
    }
    resume = true;
    startScroll();
  }
  function stop() {
    if (playing) stopScroll();
  }
  function reset() {
    if (playing) {
      stopScroll();
      startScrollOnSettle();
    }
  }
  function isPlaying() {
    return playing;
  }
  const self = {
    name: 'autoScroll',
    options: userOptions,
    init,
    destroy,
    play,
    stop,
    reset,
    isPlaying
  };
  return self;
}
AutoScroll.globalOptions = undefined;

export { AutoScroll as default };
//# sourceMappingURL=embla-carousel-auto-scroll.esm.js.map
