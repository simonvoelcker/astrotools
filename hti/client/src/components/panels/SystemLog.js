import React, { Component } from 'react'
import EventDetailsModal from '../modals/EventDetailsModal'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faExclamationTriangle } from '@fortawesome/free-solid-svg-icons'

library.add(faExclamationTriangle)


export default class SystemLog extends Component {
  constructor (props) {
    super(props)

    this.state = {
      logListOpen: false,
      selectedEventIndex: null,
    }
  }

  componentDidMount = () => {
    document.addEventListener('click', this.handleClick)
  }

  componentWillUnmount = () => {
    document.removeEventListener('click', this.handleClick)
  }

  handleClick = (event) => {
    // close log list if user clicked outside of it
    for (var i=0; i<event.path.length; i++) {
      if (event.path[i].className === 'syslog-popover') {
        return
      }
    }
    if (this.state.logListOpen) {
      this.setState({ logListOpen: false })
    }
  }

  toggleLogList = () => {
    if (!this.state.logListOpen) {
      this.context.mutations.acknowledgeEvents()
    }
    this.setState({ logListOpen: !this.state.logListOpen })
  }

  assignLogMessages (store) {
    return this.state.logListOpen ? store.logMessages : store.logMessages.slice(0, 1)
  }

  assignPosition () {
    let logMessagesLength = this.context.store.logMessages.length
    return logMessagesLength > 12 ? '-252px' : '-' + (logMessagesLength * 21) + 'px'
  }

  showDetailsModal (eventIndex) {
    this.setState({ selectedEventIndex: eventIndex })
  }

  hideDetailsModal () {
    this.setState({ selectedEventIndex: null })
  }

  renderLogEntry (entry, index) {
    const jsonEntryRegex = /(?<timestamp>.*)\s*-\s*(?<jsonbody>\{.*\})/
    const match = jsonEntryRegex.exec(entry)
    if (match === null) {
      return entry
    }

    const timestamp = match.groups.timestamp
    const eventJson = match.groups.jsonbody
    const event = JSON.parse(eventJson)

    return (
      <div>
        <span onClick={(event) => {
          if (this.state.logListOpen) {
            this.showDetailsModal(index)
            event.stopPropagation()
          }
        }}>
          {timestamp} - ⚠ <u>{event.message}</u>
        </span>
        <EventDetailsModal
          event={event}
          isOpen={this.state.selectedEventIndex === index}
          toggle={() => this.hideDetailsModal()} />
      </div>
    )
  }

  render () {
    let syslogYPos = this.state.logListOpen ? this.assignPosition() : '0px'
    let animationSpeed = this.state.logListOpen ? 'margin-top 0.5s' : 'margin-top 0.1s'
    return (
      <AppConsumer>
        {({ store }) => (
          <div data-cy='SystemLog'
               className='syslog-popover'
               style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginTop: syslogYPos, transition: animationSpeed }}
               onClick={(event) => { this.toggleLogList(); event.stopPropagation() }} >
            <ul>
              {this.assignLogMessages(store).map((logEntry, index) => {
                return <li className={'job'} key={index}>{this.renderLogEntry(logEntry, index)}</li>
              })}
            </ul>
            { store.newEventReceived &&
              <FontAwesomeIcon icon='exclamation-triangle' fixedWidth size='lg' className='static-icon' />
            }
          </div>
        )}
      </AppConsumer>
    )
  }
}

SystemLog.contextType = AppContext
