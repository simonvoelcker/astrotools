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
        onClick={() => { this.context.mutations.getAxisSpeed('RA') }}>
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
              {this.axisButton('R-', 'move-x-neg')}
              {this.axisButton('R+', 'move-x-pos')}
              {this.axisButton('D-', 'move-y-neg')}
              {this.axisButton('D+', 'move-y-pos')}
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ManualAxisControl.contextType = AppContext
