import React, { Component } from 'react'
import { AppContext, AppConsumer } from '../../context/AppContext'
import PropTypes from 'prop-types'

export default class StandardButton extends Component {
  render () {
    const { onClick, color, children, datacy, disabled, style, className } = this.props
    return (
      <AppConsumer>
        {({ store }) => (
          <button
            style={style}
            className={'btn ' + className}
            data-cy={datacy}
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

StandardButton.contextType = AppContext // This part is important to access context values

StandardButton.propTypes = {
  onClick: PropTypes.func,
  disabled: PropTypes.bool,
  color: PropTypes.string,
  className: PropTypes.string,
  datacy: PropTypes.string,
  children: PropTypes.any.isRequired,
  style: PropTypes.object
}
