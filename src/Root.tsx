import React from 'react';
import {Composition} from 'remotion';
import episode from '../episodes/generated.json';
import {Film} from './Film';
export const Root:React.FC=()=> <Composition id="HiddenEconomics" component={Film} width={episode.width} height={episode.height} fps={episode.fps} durationInFrames={episode.durationInFrames}/>;
