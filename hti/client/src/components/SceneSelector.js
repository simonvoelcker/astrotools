import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../context/AppContext'

import Icon3D from '../assets/img/icon-3D.svg'
import Gears from '../assets/img/gears.svg'
import IconInfos from '../assets/img/icon-infoscene.svg'
import IconDevelopment from '../assets/img/icon-development.svg'

export default class SceneSelector extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <div
              className={store.selectedScene === 'SceneInfos' ? 'selected scene-selector-btn' : 'scene-selector-btn'}
              onClick={() => mutations.switchScene('SceneInfos')}>
              <img src={IconInfos} data-cy={'SceneInfos'} alt={'Infos Page'} />
            </div>
            <div
              className={store.selectedScene === 'SceneProgress' ? 'selected scene-selector-btn' : 'scene-selector-btn'}
              onClick={() => mutations.switchScene('SceneProgress')}>
              <img src={Icon3D} data-cy={'SceneProgress'} alt={'Progress Page'} />
            </div>
            <div
              className={store.selectedScene === 'SceneControls' ? 'selected scene-selector-btn' : 'scene-selector-btn'}
              onClick={() => mutations.switchScene('SceneControls')}>
              <img src={Gears} data-cy={'SceneControls'} alt={'Controls Page'} />
            </div>
            <div
              className={store.selectedScene === 'SceneDevelopment' ? 'selected scene-selector-btn' : 'scene-selector-btn'}
              onClick={() => mutations.switchScene('SceneDevelopment')}>
              <img src={IconDevelopment} data-cy={'SceneDevelopment'} alt={'Development Page'} />
            </div>
          </div>
        )}

      </AppConsumer>
    )
  }
}

SceneSelector.contextType = AppContext
