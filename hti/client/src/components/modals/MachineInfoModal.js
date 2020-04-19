import React, { Component } from 'react'
import { Modal, TabContent, TabPane, Nav, NavItem, NavLink } from 'reactstrap'
import { AppContext, AppConsumer } from '../../context/AppContext'
import PropTypes from 'prop-types'
import GeneralInfoBody from './GeneralInfoBody'
import SensorInfoBody from './SensorInfoBody'
import StandardButton from '../panels/StandardButton'

export default class MachineInfoModal extends Component {
  constructor (props) {
    super(props)

    this.toggle = this.toggle.bind(this)
    this.state = {
      activeTab: '1'
    }
  }

  toggle (tab) {
    if (this.state.activeTab !== tab) {
      this.setState({
        activeTab: tab
      })
    }
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showMachineInfoModal')} className='machine-info-modal' data-cy='MachineInfoModal'>
            <Nav tabs className='nav'>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '1' ? 'btn' : 'btn tab-link'}
                  onClick={() => { this.toggle('1') }}
                  data-cy='GeneralInfoTab'
                >
                  General Machine Information
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '2' ? 'btn' : 'btn tab-link'}
                  onClick={() => { this.toggle('2') }}
                  data-cy='SensorInfoTab'
                >
                  Sensor Information
                </NavLink>
              </NavItem>
            </Nav>
            <TabContent activeTab={this.state.activeTab}>
              <TabPane tabId='1' data-cy='GeneralInfo'>
                <GeneralInfoBody />
              </TabPane>
              <TabPane tabId='2' data-cy='SensorInfo'>
                <SensorInfoBody />
              </TabPane>
              <StandardButton
                onClick={() => { mutations.toggleModal('showMachineInfoModal') }}
                style={{ width: 'auto', margin: '10px', float: 'right' }}
              >
                Close
              </StandardButton>
            </TabContent>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

SensorInfoBody.contextType = AppContext

SensorInfoBody.propTypes = {
  toggle: PropTypes.bool
}
