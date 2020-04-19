import React, { Component } from 'react'
import { Spinner } from 'reactstrap'
import { AppContext, AppConsumer } from '../../context/AppContext'
import PropTypes from 'prop-types'

export default class SpinnerButton extends Component {
  render () {
    const { disabled, onClick, request, children, datacy } = this.props
    return (
      <AppConsumer>
        {({ store }) => (
          <button
            data-cy={datacy}
            className={store.pendingRequest === request || (store.runningCommand && store.runningCommand.id === request) ? 'btn progressbar' : 'btn'}
            disabled={disabled || store.pendingRequest === request || (store.runningCommand && store.runningCommand.id === request)}
            onClick={onClick}
            onContextMenu={(e) => {
              e.preventDefault()
              onClick()
            }}>
            {store.pendingRequest === request ? <Spinner color='light' size='sm' /> : ''} {children}
          </button>
        )}
      </AppConsumer>
    )
  }
}

SpinnerButton.contextType = AppContext // This part is important to access context values

SpinnerButton.propTypes = {
  disabled: PropTypes.bool,
  onClick: PropTypes.func,
  request: PropTypes.string,
  datacy: PropTypes.string,
  children: PropTypes.string
}
