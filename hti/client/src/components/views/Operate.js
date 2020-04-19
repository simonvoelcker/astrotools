import React, { Component } from 'react'

import SceneSelector from '../SceneSelector'
import SceneControls from '../scenes/SceneControls'
import SceneProgress from '../scenes/SceneProgress'
import SceneInfos from '../scenes/SceneInfos'
import SceneDevelopment from '../scenes/SceneDevelopment'
import SplashScreen from '../panels/SplashScreen'
import StatusPanel from '../panels/StatusPanel'
import { AppConsumer, AppContext } from '../../context/AppContext'
import VersionInfo from '../../components/panels/VersionInfo'
import SystemLog from '../../components/panels/SystemLog'
import { createPrintEndDateString } from '../../Utils'
import ModalManager from '../../components/ModalManager'


export default class Operate extends Component {
  constructor (props) {
    super(props)

    this.state = {
      currentTime: ''
    }
  }

  componentDidMount () {
    this.updateTimes()
    this.timerID = setInterval(() => this.updateTimes(), 1000)
  }

  updateTimes () {
    this.setState({ currentTime: createPrintEndDateString(0) })
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <VersionInfo />
            {store.InitialDataLoaded ? this.content(store, mutations) : <SplashScreen />}
          </div>
        )}
      </AppConsumer>
    )
  }

  content (store, mutations) {
    const { currentTime } = this.state
    return (
      <div className='operate'>
        <div style={{ display: 'flex', flexDirection: 'row', flexGrow: '1', height: '718px' }}>
          <div className='column column-left'>
            <div style={{ position: 'absolute', top: '15px', left: '35px' }}>
              {currentTime.split(',')[0]}
              <br />{currentTime.split(',')[1]}
            </div>
            <SceneSelector />
          </div>
          <div className='column column-center'>
            <SceneProgress />
            {(function () {
              switch (store.selectedScene) {
                case 'SceneControls':
                  return <SceneControls />
                case 'SceneInfos':
                  return <SceneInfos />
                case 'SceneDevelopment':
                  return <SceneDevelopment />
                default:
                  return null
              }
            })()}
          </div>
        </div>
        <div className='footer'>
          <SystemLog />
          <StatusPanel />
        </div>
        <ModalManager />
      </div>
    )
  }
}
Operate.contextType = AppContext // This part is important to access context values
