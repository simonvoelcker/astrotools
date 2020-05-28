import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

export default class AxisControl extends Component {
  constructor(props) {
    super(props)

    this.incrementOptions = [
      {label: 'slow',   dps: 0.1 / 3600.0},
      {label: 'medium', dps: 0.1 / 60.0},
      {label: 'fast',   dps: 0.1},
    ]

    this.state = {
      increment: this.incrementOptions[0]
    }
  }

  componentDidMount () {
    document.onkeydown = this.onKeyDown.bind(this)
  }

  onKeyDown (event) {
    switch (event.key) {
        case 'ArrowUp':
            this.steer('up')
            break;
        case 'ArrowDown':
            this.steer('down')
            break;
        case 'ArrowLeft':
            this.steer('left')
            break;
        case 'ArrowRight':
            this.steer('right')
            break;
        default:
            break;
    }
  }

  rest () {
    this.context.mutations.setRest()
  }

  stop () {
    this.context.mutations.setSpeeds(0.0, 0.0)
  }

  steer (direction) {
    if (this.context.store.axisSpeeds === null) {
      return
    }

    const increments = {
      up: {ra: 0.0, dec: -this.state.increment.dps},
      down: {ra: 0.0, dec: +this.state.increment.dps},
      left: {ra: -this.state.increment.dps, dec: 0.0},
      right: {ra: +this.state.increment.dps, dec: 0.0},
    }[direction]

    this.context.mutations.setSpeeds(
      this.context.store.axisSpeeds.raDps + increments.ra,
      this.context.store.axisSpeeds.decDps + increments.dec,
    )
  }

  formatAxisSpeed (dps) {
    if (dps === null) {
      return {value: 0, unit: ''}
    }
    if (Math.abs(dps) >= 0.5) {
      return {value: dps, unit: '°/s'}
    }
    let dph = dps * 3600.0
    return {value: dph, unit: '°/h'}
  }

  render () {
    const store = this.context.store
    const raSpeed = this.formatAxisSpeed(store.axisSpeeds ? store.axisSpeeds.raDps : null)
    const decSpeed = this.formatAxisSpeed(store.axisSpeeds ? store.axisSpeeds.decDps : null)

    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel axis-control-panel'>
              <div className='button-column'>
                <span className='spaced-text'>{store.axisSpeeds ? store.axisSpeeds.mode.toUpperCase() : '-'}</span>
                <StandardButton
                  disabled={store.axisSpeeds && store.axisSpeeds.mode === 'resting'}
                  onClick={this.rest.bind(this)}>REST</StandardButton>
                <StandardButton
                  disabled={!store.axisSpeeds || store.axisSpeeds.mode === 'stopped'}
                  onClick={this.stop.bind(this)}>STOP</StandardButton>
              </div>
              <div className='steering-control'>
                <StandardButton className='btn steer-left' onClick={() => this.steer('left')}>&#129136;</StandardButton>
                <StandardButton className='btn steer-right' onClick={() => this.steer('right')}>&#129138;</StandardButton>
                <StandardButton className='btn steer-up' onClick={() => this.steer('up')}>&#129137;</StandardButton>
                <StandardButton className='btn steer-down' onClick={() => this.steer('down')}>&#129139;</StandardButton>
                <span className='spaced-text steer-left-label'>
                  {raSpeed.value < 0 ? -raSpeed.value.toFixed(1) + raSpeed.unit : ''}
                </span>
                <span className='spaced-text steer-right-label'>
                  {raSpeed.value > 0 ? raSpeed.value.toFixed(1) + raSpeed.unit : ''}
                </span>
                <span className='spaced-text steer-up-label'>
                  {decSpeed.value < 0 ? -decSpeed.value.toFixed(1) + decSpeed.unit : ''}
                </span>
                <span className='spaced-text steer-down-label'>
                  {decSpeed.value > 0 ? decSpeed.value.toFixed(1) + decSpeed.unit : ''}
                </span>
              </div>
              <div className='button-column'>
                <UncontrolledDropdown>
                  <DropdownToggle caret>{this.state.increment.label}</DropdownToggle>
                  <DropdownMenu>
                    {this.incrementOptions.map(option => {
                      return <DropdownItem key={option.label} onClick={() => {this.setState({increment: option})}}>
                        {option.label}
                      </DropdownItem>
                    })}
                  </DropdownMenu>
                </UncontrolledDropdown>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AxisControl.contextType = AppContext
