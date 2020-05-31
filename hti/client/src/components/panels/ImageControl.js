import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import StandardButton from '../panels/StandardButton'

export default class ImageControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }
  }

  render () {
    let path = this.context.store.imagePath
    let components = path.split('/')
    let pathComponents = components.splice(0, components.length-1)
    let filename = components[components.length-1]

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <div className='panel image-control-panel'>
              {pathComponents.map(component => {
                return <UncontrolledDropdown className='path-dropdown'>
                 <DropdownToggle caret>{component}</DropdownToggle>
                 <DropdownMenu>
                   <DropdownItem key={component} onClick={() => {}}>{component}</DropdownItem>
                 </DropdownMenu>
               </UncontrolledDropdown>
               })}
             <span className='spaced-text image-filename'>{filename}</span>
             <StandardButton className='btn image-btn' onClick={() => {}}>&#x23F4;</StandardButton>
             <StandardButton className='btn image-btn' onClick={() => {}}>&#x23F5;</StandardButton>
             <StandardButton className='btn image-btn' onClick={() => {}}>&#129517;</StandardButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ImageControl.contextType = AppContext
