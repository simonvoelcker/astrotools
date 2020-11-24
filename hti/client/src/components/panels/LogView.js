import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class LogView extends Component {

  render () {

    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel log-panel'>
              <span className='spaced-text'>Log</span>
              <ul>
                {store.logEntries.map(logEntry => {
                  return <li>{logEntry.text}</li>
                })}
              </ul>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

LogView.contextType = AppContext
