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
    const incrementDps = 0.1 / 3600.0

    const increments = {
      up: {ra: 0.0, dec: -incrementDps},
      down: {ra: 0.0, dec: +incrementDps},
      left: {ra: -incrementDps, dec: 0.0},
      right: {ra: +incrementDps, dec: 0.0},
    }[direction]

    this.context.mutations.setSpeeds(
      this.context.store.axisSpeeds.raDps + increments.ra,
      this.context.store.axisSpeeds.decDps + increments.dec,
    )
  }

  render () {
    const store = this.context.store
    let raSpeed = 0
    let decSpeed = 0
    if (store.axisSpeeds) {
      // degrees per second -> degrees per hour
      raSpeed = store.axisSpeeds.raDps * 3600.0
      decSpeed = store.axisSpeeds.decDps * 3600.0
    }

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
                <span className='spaced-text steer-left-label'>
                  {raSpeed < 0 ? -raSpeed.toFixed(1) + '°/h' : ''}
                </span>
                <span className='spaced-text steer-right-label'>
                  {raSpeed > 0 ? raSpeed.toFixed(1) + '°/h' : ''}
                </span>
                <span className='spaced-text steer-up-label'>
                  {decSpeed < 0 ? -decSpeed.toFixed(1) + '°/h' : ''}
                </span>
                <span className='spaced-text steer-down-label'>
                  {decSpeed > 0 ? decSpeed.toFixed(1) + '°/h' : ''}
                </span>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AxisControl.contextType = AppContext
