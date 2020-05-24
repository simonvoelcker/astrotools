import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'

export default class AxisControl extends Component {
  rest () {
    this.context.mutations.setRest()
  }

  stop () {
    this.context.mutations.setSpeeds(0.0, 0.0)
  }

  steer (direction) {
    // this.context.mutations.setSpeeds(this.state.raSpeed, this.state.decSpeed)
  }

  render () {
    // const raDrift = 3600.0 * this.context.store.axisSpeeds.raDps
    // steering, resting or stopping.

    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel axis-control-panel'>
              <div className='button-column'>
                <span className='spaced-text'>Mode: {store.axisSpeeds ? store.axisSpeeds.mode.toUpperCase() : '-'}</span>
                <StandardButton
                  disabled={store.axisSpeeds && store.axisSpeeds.mode === 'resting'}
                  onClick={this.rest.bind(this)}>REST</StandardButton>
                <StandardButton
                  disabled={!store.axisSpeeds || store.axisSpeeds.mode === 'stopped'}
                  onClick={this.stop.bind(this)}>STOP</StandardButton>
              </div>
              <div className='steering-control'>
                <StandardButton className='btn steer-left' onClick={() => this.steer('left')}>L</StandardButton>
                <StandardButton className='btn steer-right' onClick={() => this.steer('right')}>R</StandardButton>
                <StandardButton className='btn steer-up' onClick={() => this.steer('up')}>U</StandardButton>
                <StandardButton className='btn steer-down' onClick={() => this.steer('down')}>D</StandardButton>
                <span className='spaced-text steer-left-label'>0.2°/h</span>
                <span className='spaced-text steer-right-label'>0.2°/h</span>
                <span className='spaced-text steer-up-label'>0.2°/h</span>
                <span className='spaced-text steer-down-label'>0.2°/h</span>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AxisControl.contextType = AppContext
