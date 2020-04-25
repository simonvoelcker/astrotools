import React, { Component } from 'react'
import { AppContext, AppConsumer } from '../../context/AppContext'

export default class StandardButton extends Component {
  render () {
    const { onClick, color, children, disabled, style, className } = this.props
    return (
      <AppConsumer>
        {({ store }) => (
          <button
            style={style}
            className={'btn ' + className}
            disabled={disabled}
            color={color}
            onClick={onClick}
            onContextMenu={(e) => {
              e.preventDefault()
              onClick()
            }}>
            {children}
          </button>
        )}
      </AppConsumer>
    )
  }
}

StandardButton.contextType = AppContext
