import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

export default class ImageControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
      datePathComponent: '2020-03-15',
      typePathComponent: 'lights',
      namePathComponent: '20200315-164512.jpg'
    }
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <div className='panel image-control-panel'>
              <UncontrolledDropdown>
               <DropdownToggle caret>{this.state.datePathComponent}</DropdownToggle>
               <DropdownMenu>
                 <DropdownItem onClick={() => {}}>{this.state.datePathComponent}</DropdownItem>
               </DropdownMenu>
             </UncontrolledDropdown>
              <UncontrolledDropdown>
               <DropdownToggle caret>{this.state.typePathComponent}</DropdownToggle>
               <DropdownMenu>
                 <DropdownItem onClick={() => {}}>{this.state.typePathComponent}</DropdownItem>
               </DropdownMenu>
             </UncontrolledDropdown>
             <span className='spaced-text'>{this.state.namePathComponent}</span>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ImageControl.contextType = AppContext
