import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import $backend from '../../backend'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';


export default class FocusControl extends Component {
  constructor (props) {
    super(props)

    this.state = {
      increment: 1000
    }
  }

  render () {
    const store = this.context.store
    const panelStateClass = store.axesSim ? 'panel-yellow' : (store.axesConnected ? 'panel-green' : 'panel-red')

    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel focus-control-panel ' + panelStateClass}>
            <div className='button-column'>
              <span className='spaced-text'>Focus Control</span>
              <div className='button-row'>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.autoFocus()}}>Auto</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(+this.state.increment)}}>+</StandardButton>
                <StandardButton
                  disabled={!store.axesSim && !store.axesConnected}
                  onClick={() => {$backend.moveFocus(-this.state.increment)}}>-</StandardButton>
                <UncontrolledDropdown>
                  <DropdownToggle caret>{this.state.increment}</DropdownToggle>
                  <DropdownMenu>
                    <DropdownItem onClick={() => {this.setState({increment: 1000})}}>1000</DropdownItem>
                    <DropdownItem onClick={() => {this.setState({increment: 100})}}>100</DropdownItem>
                    <DropdownItem onClick={() => {this.setState({increment: 10})}}>10</DropdownItem>
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

FocusControl.contextType = AppContext
