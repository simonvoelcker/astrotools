import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import StandardButton from '../panels/StandardButton'

export default class ImageControl extends Component {

  render () {
    let prefix = '-', filename = '-', directory = '-'
    let path = this.context.utils.imagePath()
    if (path !== null) {
      [ prefix, directory, filename ] = path.split('/')
    }

    return (
      <AppConsumer>
        {({ store, mutations, utils }) => (
          <div>
            <div className='panel image-control-panel'>
              <span className='spaced-text'>{prefix}</span>
              <UncontrolledDropdown className='path-dropdown'>
                <DropdownToggle caret>{directory}</DropdownToggle>
                <DropdownMenu>
                {utils.directoryNames().map(dir => {
                  return <DropdownItem key={dir} onClick={() => {mutations.selectDirectory(dir)}}>{dir}</DropdownItem>
                })}
                </DropdownMenu>
              </UncontrolledDropdown>
              <span className='spaced-text image-filename'>{filename}</span>
              <span className='spaced-text'>{store.imageSelection.filenameIndex+1}/{utils.numFiles()}</span>
              <StandardButton className='btn image-btn' onClick={mutations.selectPreviousImage}>&#x23F4;</StandardButton>
              <StandardButton className='btn image-btn' onClick={mutations.selectNextImage}>&#x23F5;</StandardButton>
              <StandardButton className='btn image-btn' onClick={() => {}}>&#8689;</StandardButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ImageControl.contextType = AppContext
