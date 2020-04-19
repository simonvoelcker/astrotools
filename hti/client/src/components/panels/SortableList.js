import React from 'react'
import { SortableContainer, SortableElement } from 'react-sortable-hoc'
import JobListItem from '../../components/panels/JobListItem'
import UploadListItem from '../../components/panels/UploadListItem'

const SortableItem = SortableElement(({ value, printProgress, display }) => {
  return (
    <div style={{ margin: '5px 0' }}>
      <JobListItem job={value} printProgress={printProgress} display={display} />
    </div>
  )
})

const SortableList = SortableContainer(({ scene, printProgress, items }) => {
  const display = !(scene === 'SceneInfos')
  return (
    <ul style={{ padding: '0' }}>
      <div style={{ margin: '5px 0' }}>
        <UploadListItem />
      </div>
      {
        items.map((job, index) => {
          return <SortableItem key={`item-${index}`} index={index} value={job} printProgress={printProgress} display={display} />
        })
      }
    </ul>
  )
})

export {
  SortableList
}
