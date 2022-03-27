import React, { Component, useState } from 'react'

import CameraView from '../panels/CameraView'
import LogView from '../panels/LogView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import GoToControl from '../panels/GoToControl'
import PECControl from '../panels/PECControl'
import FocusControl from '../panels/FocusControl'
import GuidingControl from '../panels/GuidingControl'

import AnalyzeTab from '../tabs/AnalyzeTab'
import StackTab from '../tabs/StackTab'

import { AppConsumer, AppContext } from '../../appstate'
import { TabContent, TabPane, Nav, NavItem, NavLink, Card, Button, CardTitle, CardText, Row, Col } from 'reactstrap';

export default class Operator extends Component {

  constructor (props) {
    super(props)
    this.state = {
      activeTab: '7',
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
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '6' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('6'); }}
                >
                  Analyze
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink
                  className={this.state.activeTab === '7' ? 'active' : ''}
                  onClick={() => { this.setActiveTab('7'); }}
                >
                  Stack
                </NavLink>
              </NavItem>
            </Nav>
            <TabContent activeTab={this.state.activeTab}>

              <TabPane tabId="2">
                <div className='capturing-tab'>
                  <div className='left-column'>
                    <CameraView camera={store.capturingCamera} />
                  </div>
                  <div className='right-column'>
                    <CaptureControl camera={store.capturingCamera} />
                    <FocusControl />
                    <AxisControl />
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
                    <GuidingControl camera={store.guidingCamera} />
                  </div>
                </div>
              </TabPane>

              <TabPane tabId="4">
                <div className='controls-tab'>
                  <GoToControl />
                  <AxisControl />
                </div>
              </TabPane>

              <TabPane tabId="5">
                <div className='log-tab'>
                  <LogView />
                </div>
              </TabPane>

              <TabPane tabId="6">
                <AnalyzeTab />
              </TabPane>

              <TabPane tabId="7">
                <StackTab />
              </TabPane>

            </TabContent>
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operator.contextType = AppContext
