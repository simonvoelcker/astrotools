import React, { Component } from 'react'
import { Modal, TabContent, TabPane, Nav, NavItem, NavLink, Row, Col, ModalBody } from 'reactstrap'
import { AppContext, AppConsumer } from '../../context/AppContext'
import PropTypes from 'prop-types'
import StandardButton from '../panels/StandardButton'

export default class NetworkInfoModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showNetworkInfoModal')} className='machine-info-modal' data-cy='NetworkInfoModal'>
            <Nav tabs className='nav'>
              <NavItem>
                <NavLink
                  className='btn'
                  data-cy='NetworkInfoTab'>
                  Network Information
                </NavLink>
              </NavItem>
            </Nav>
            <TabContent activeTab='1'>
              <TabPane tabId='1' data-cy='NetworkInfo'>
                <ModalBody>
                  {
                    store.networkInfo && (
                      store.networkInfo.map((infos, index) => (
                        infos['inet'] &&
                        <div className='network-info-rows' key={index}>
                          { Object.keys(infos).map((key) => (
                              <Row key={key+index}>
                                 <Col sm={2}>{key}</Col>
                                 <Col sm={6}>{infos[key]}</Col>
                              </Row>
                            ))
                          }
                          <Row>
                          </Row>
                        </div>
                      ))
                    )
                  }
                </ModalBody>
              </TabPane>
              <StandardButton
                onClick={() => { mutations.toggleModal('showNetworkInfoModal') }}
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

NetworkInfoModal.contextType = AppContext

NetworkInfoModal.propTypes = {
  toggle: PropTypes.bool
}
