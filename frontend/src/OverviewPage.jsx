import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  EuiHeader,
  EuiHeaderSection,
  EuiHeaderSectionItem,
  EuiHeaderBreadcrumbs,
  EuiPageBody,
  EuiPage,
  EuiPageHeader,
  EuiButton,
  EuiCode,
  EuiBasicTable,
  EuiLink,
} from '@elastic/eui';

const OverviewPage = () => {
  const breadcrumbs = [
    {
      text: 'Paperwrite',
      href: "/"
    },
    {
      text: 'Knowledge Graphs',
    },
  ];

  const columns = [
    {
      field: "kid",
      name: "Id",
      sortable: true,
      render: (kid) => {
        return (
          <>
            {kid} (<EuiLink href={`http://127.0.0.1:44777/kng/${kid}/visualisation.html`} external>visualise</EuiLink>, <EuiLink href={`/#/details?kid=${kid}`}>details</EuiLink>)
          </>
        )
      },
      valign: "top",
    },
    {
      field: "size",
      name: "Size",
      valign: "top",
    },
    {
      field: "created",
      name: "Created",
      valign: "top",
    },
    {
      field: "knowledge_base",
      name: "Knowledge Base",
      render: (pdfs) => (<>{pdfs.map((str) => { return <>{str}<br /></> })}</>),
      valign: "top"
    },
  ];
  const [items, setItems] = useState([])

  useEffect(() => {
    axios.get("http://127.0.0.1:44777/kng/list")
      .then(resp => {
        if (resp.status === 200) {
          setItems(resp.data)
        }
      })
  }, []);

  return (
    <>
      <EuiHeader position="fixed">
        <EuiHeaderBreadcrumbs
          aria-label="Header breadcrumbs example"
          breadcrumbs={breadcrumbs}
        />
        <EuiHeaderSection side="right">
          <EuiHeaderSectionItem>
            <EuiCode>version: 0.0.1</EuiCode>
          </EuiHeaderSectionItem>
        </EuiHeaderSection>
      </EuiHeader>
      <EuiHeader />

      <EuiPage paddingSize="l">
        <EuiPageBody>
          <EuiPageHeader
            bottomBorder
            pageTitle="Knowledge Graphs"
            description="Starting site with list of all knowledge graph currently stored in backend. To add a new knowledge graph click the button on the right."
            rightSideItems={[
              <EuiButton href='/#/create_new'>Add New Kowledge Graph</EuiButton>
            ]}
          />

          <EuiBasicTable
            columns={columns}
            rowCount={10}
            tableLayout="auto"
            items={items}
          />

        </EuiPageBody>
      </EuiPage>
    </>
  );
};

export default OverviewPage;