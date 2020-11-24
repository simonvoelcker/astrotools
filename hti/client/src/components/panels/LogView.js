import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class LogView extends Component {

  formatTimestamp (timestamp) {
    const date = new Date(timestamp)
    const hours = '0' + date.getHours()
    const minutes = '0' + date.getMinutes()
    const seconds = '0' + date.getSeconds()
    return hours.substr(-2) + ':' + minutes.substr(-2) + ':' + seconds.substr(-2)
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel log-panel'>
              <span className='spaced-text'>Log</span>
              <div className='entries-list'>
                {store.logEntries.map(entry => {
                  return <span>{this.formatTimestamp(entry.timestamp)}: {entry.text}</span>
                })}
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

LogView.contextType = AppContext
