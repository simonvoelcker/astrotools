import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Col } from 'reactstrap'

export default class PrintingStatusIndicator extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <Col sm={3}>
            <div data-cy='PrintingStatusIndicator'>
              {
                store.printingNow
                  ? store.isPaused
                    ? store.isHeatingUp
                      ? <div><h4><span style={{ color: 'red' }}>●</span> Heating Up</h4>
                      <h4><span style={{ color: 'yellow' }}>●</span> Resuming</h4></div>
                      : <h2 style={{ marginTop: '8px' }}><span style={{ color: 'yellow' }}>●</span> Paused</h2>
                    : store.isHeatingUp
                      ? <h2 style={{ marginTop: '8px' }}><span style={{ color: 'red' }}>●</span> Heating Up</h2>
                      : <h2 style={{ marginTop: '8px' }}><span style={{ color: 'green' }}>●</span> Running</h2>
                  : ''
              }
            </div>
          </Col>
        )}
      </AppConsumer>
    )
  }
}

PrintingStatusIndicator.contextType = AppContext
