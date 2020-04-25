import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class ManualAxisControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }
  }

  axisButton = (axis, cssClass) => {
    return (
      <StandardButton
        className={cssClass}
        disabled={false}
        onClick={() => { console.log("moving axis " + axis) }}>
        { axis }
      </StandardButton>
    )
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div>Manual Axis Control</div>
            <div className='axis-move-panel'>
              {this.axisButton('X-', 'move-x-neg')}
              {this.axisButton('X+', 'move-x-pos')}
              {this.axisButton('Y-', 'move-y-neg')}
              {this.axisButton('Y+', 'move-y-pos')}
              {this.axisButton('Z-', 'move-z-neg')}
              {this.axisButton('Z+', 'move-z-pos')}
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ManualAxisControl.contextType = AppContext
