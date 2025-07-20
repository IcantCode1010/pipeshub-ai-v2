import { CreateOptionsType } from 'embla-carousel';
export type OptionsType = CreateOptionsType<{
    direction: 'forward' | 'backward';
    speed: number;
    startDelay: number;
    playOnInit: boolean;
    stopOnFocusIn: boolean;
    stopOnInteraction: boolean;
    stopOnMouseEnter: boolean;
    rootNode: ((emblaRoot: HTMLElement) => HTMLElement | null) | null;
}>;
export declare const defaultOptions: OptionsType;
