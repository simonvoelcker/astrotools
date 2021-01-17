import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import $backend from '../../backend'


export default class FocusControl extends Component {
  render () {
    const store = this.context.store
    const panelStateClass = store.axesSim ? 'panel-yellow' : (store.axesConnected ? 'panel-green' : 'panel-red')

    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel focus-control-panel ' + panelStateClass}>
            <div className='button-column'>
              <span className='spaced-text'>Focus Control</span>
              <div className='button-row'>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(-1000)}}>-1000</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(-100)}}>-100</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(-10)}}>-10</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(+10)}}>+10</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(+100)}}>+100</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(+1000)}}>+1000</StandardButton>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

FocusControl.contextType = AppContext
