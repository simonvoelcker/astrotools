import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import $backend from '../../backend'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';


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
                <button className='btn'
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(+1000)}}>+10</button>
                <button className='btn'
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(+100)}}>+1</button>
                <button className='btn'
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(-100)}}>-1</button>
                <button className='btn'
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(-1000)}}>-10</button>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

FocusControl.contextType = AppContext
