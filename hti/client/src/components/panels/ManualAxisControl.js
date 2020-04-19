import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class ManualAxisControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
      mode: '100mm'
    }
  }

  disabledControl = () => {
    let store = this.context.store
    return !store.doorStatus.doorLocked || store.pendingRequest !== null || store.printingNow || store.mode === 'demo'
  }

  axisButton = (axis, cssClass) => {
    return (
      <StandardButton
        className={cssClass}
        disabled={this.disabledControl()}
        onClick={() => { this.context.mutations.moveAxis(axis, this.state.mode) }}>
        { axis }
      </StandardButton>
    )
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div>Manual Axis Control{store.doorStatus.doorLocked ? '' : <span style={{ color: 'red' }}> - Lock doors to use</span>}</div>
            <div className='axis-move-panel'>
              <div>
                {this.axisButton('X-', 'move-x-neg')}
                {this.axisButton('X+', 'move-x-pos')}
                {this.axisButton('Y-', 'move-y-neg')}
                {this.axisButton('Y+', 'move-y-pos')}
                {this.axisButton('Z-', 'move-z-neg')}
                {this.axisButton('Z+', 'move-z-pos')}
              </div>
              <div className='move-amount'>
                <StandardButton
                  className={this.state.mode === '1mm' ? 'btn-selected' : ''}
                  disabled={this.disabledControl()}
                  onClick={() => { this.setState({ mode: '1mm' }) }}>1 mm</StandardButton>
                <StandardButton
                  className={this.state.mode === '10mm' ? 'btn-selected' : ''}
                  disabled={this.disabledControl()}
                  onClick={() => { this.setState({ mode: '10mm' }) }}>10 mm</StandardButton>
                <StandardButton
                  className={this.state.mode === '100mm' ? 'btn-selected' : ''}
                  disabled={this.disabledControl()}
                  onClick={() => { this.setState({ mode: '100mm' }) }}>100 mm</StandardButton>

              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ManualAxisControl.contextType = AppContext
