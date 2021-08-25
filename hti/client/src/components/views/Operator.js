import React, { Component, useState } from 'react'

import CameraView from '../panels/CameraView'
import LogView from '../panels/LogView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import TrackingControl from '../panels/TrackingControl'
import PECControl from '../panels/PECControl'
import FocusControl from '../panels/FocusControl'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { TabContent, TabPane, Nav, NavItem, NavLink, Card, Button, CardTitle, CardText, Row, Col } from 'reactstrap';

export default class Operator extends Component {

  constructor (props) {
    super(props)
    this.state = {
      activeTab: '1',
    }
  }

  setActiveTab (tab) {
    this.setState({activeTab: tab})
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='operator'>
            <Nav tabs>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '1' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('1'); }}
                >
                  Overview
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '2' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('2'); }}
                >
                  Capturing
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '3' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('3'); }}
                >
                  Guiding
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '4' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('4'); }}
                >
                  Control
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '5' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('5'); }}
                >
                  Log
                </NavLink>
              </NavItem>
            </Nav>
            <TabContent activeTab={this.state.activeTab}>

              <TabPane tabId="1">
                <div className='all-controls-tab'>
                  <div className='left-column'>
                    <CameraView camera={store.capturingCamera} />
                    <LogView />
                  </div>
                  <div className='right-column'>
                    <TrackingControl />
                    <CaptureControl camera={store.capturingCamera} />
                    <FocusControl />
                    <AxisControl />
                  </div>
                </div>
              </TabPane>

              <TabPane tabId="2">
                <div className='capturing-tab'>
                  <div className='left-column'>
                    <CameraView camera={store.capturingCamera} />
                  </div>
                  <div className='right-column'>
                    <CaptureControl camera={store.capturingCamera} />
                    <FocusControl />
                  </div>
                </div>
              </TabPane>

              <TabPane tabId="3">
                <div className='guiding-tab'>
                  <div className='left-column'>
                    <CameraView camera={store.guidingCamera} />
                  </div>
                  <div className='right-column'>
                    <CaptureControl camera={store.guidingCamera} />
                  </div>
                </div>
              </TabPane>

              <TabPane tabId="4">
                <div className='controls-tab'>
                  <TrackingControl />
                  <AxisControl />
                </div>
              </TabPane>

              <TabPane tabId="5">
                <div className='log-tab'>
                  <LogView />
                </div>
              </TabPane>

            </TabContent>
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operator.contextType = AppContext
