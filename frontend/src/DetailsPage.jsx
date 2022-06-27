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
  EuiCode,
  EuiDescriptionList,
  EuiLink,
  EuiButton,
  EuiSpacer,
  EuiFieldSearch,
  EuiText
} from '@elastic/eui';

const queryString = require('query-string');

const DetailsPage = () => {
  const href = window.location.href.replace("/#", "");
  const url = queryString.parseUrl(href)
  const kid = url.query.kid

  const breadcrumbs = [
    {
      text: 'Paperwrite',
      href: "/"
    },
    {
      text: 'Knowledge Graphs',
      href: "/"
    },
    {
      text: kid
    }
  ];
  const [items, setItems] = useState([])
  const [update, setUpdate] = useState(0)
  const [predict, setPredict] = useState(null)
  const [sentence, setSentence] = useState("")

  useEffect(() => {
    axios.get(`http://127.0.0.1:44777/kng/${kid}/details`)
      .then(resp => {
        if (resp.status === 200) {
          setItems([
            {
              title: "Actions",
              description: <>
                <EuiButton
                  href={`/#/details?kid=${kid}`}
                  style={{ marginRight: "8px" }}
                >Details</EuiButton>
                <EuiButton
                  style={{ marginRight: "8px" }}
                  onClick={() => {
                    axios.get(`http://127.0.0.1:44777/kng/${kid}/train_model`)
                      .then(resp => {
                        if (resp.status === 200) {
                          setUpdate(update + 1);
                        }
                      })
                  }}
                >Train AI Model</EuiButton>
                <EuiButton
                  href={`http://127.0.0.1:44777/kng/${kid}/visualisation.html`}
                  external
                >Visualisation</EuiButton>
              </>
            },
            {
              title: "ID",
              description: <><EuiCode>{resp.data.kid}</EuiCode></>,
            },
            {
              title: "Size",
              description: resp.data.size
            },
            {
              title: "Created at",
              description: resp.data.created,
            },
            {
              title: "AI Models",
              description: (
                <>
                  {resp.data.ai_models}
                  <EuiSpacer size='s' />
                  <div style={{ display: "flex" }}>
                    <EuiFieldSearch
                      value={sentence}
                      onChange={(e) => { setSentence(e.target.value); setUpdate(update + 1) }}
                      disabled={resp.data.ai_models === "none" && true}
                    />
                    <div style={{ width: 8 }} />
                    <EuiButton
                      onClick={() => {
                        axios.post(`http://127.0.0.1:44777/kng/${kid}/predict`, { "sentence": sentence })
                          .then(resp => {
                            setPredict(resp.data.predit_val)
                            setUpdate(update + 1)
                          })
                          .catch(error => {
                            setPredict(error.response.data.predit_val)
                            setUpdate(update + 1)
                          })
                      }}
                      disabled={resp.data.ai_models === "none" && true}
                    >Predict</EuiButton>

                  </div>
                  <EuiSpacer size='s' />
                  {predict !== null &&
                    <EuiText size='xl'>Prediction Value: <EuiCode>{predict}</EuiCode></EuiText>
                  }
                </>
              ),
            },
            {
              title: "Knowledge Base",
              description: (
                <>
                  {resp.data.knowledge_base.map((kb) => {
                    return <>{kb}<br /></>
                  })}
                </>
              )
            },
          ]);
        }
      })
  }, [update]);

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
            pageTitle={<>Knowledge Graph: <EuiCode>{kid}</EuiCode></>}
            description="Details of a specific knowledge graph and functions for it."
          />

          <EuiDescriptionList
            listItems={items}
          />

        </EuiPageBody>
      </EuiPage>
    </>
  );
};

export default DetailsPage;