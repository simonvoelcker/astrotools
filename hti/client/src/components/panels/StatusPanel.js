import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDoorClosed, faDoorOpen, faLock, faLockOpen, faHome, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons'

library.add(faDoorClosed, faDoorOpen, faLock, faLockOpen, faHome, faCheck, faTimes)

export default class StatusPanel extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='status-panel'>
            { !store.doorStatus.doorOpen
              ? <div><FontAwesomeIcon icon='door-closed' fixedWidth size='lg' className='static-icon' /></div>
              : <div><FontAwesomeIcon icon='door-open' fixedWidth size='lg' className='blinking-icon' /></div>
            }
            { store.doorStatus.doorLocked
              ? <div><FontAwesomeIcon icon='lock' fixedWidth size='lg' className='static-icon' /></div>
              : <div><FontAwesomeIcon icon='lock-open' fixedWidth size='lg' className='blinking-icon' /></div>
            }
            { store.machineHomed
              ? <div><FontAwesomeIcon icon='home' fixedWidth size='lg' className='static-icon' /></div>
              : <div><FontAwesomeIcon icon='home' fixedWidth size='lg' className='blinking-icon' /></div>
            }
          </div>
        )}
      </AppConsumer>
    )
  }
}

StatusPanel.contextType = AppContext
