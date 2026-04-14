// Import for type checking
import {
  AddItemButton,
  type ApiFormFieldSet,
  apiUrl,
  checkPluginVersion,
  type InvenTreePluginContext,
  InvenTreeTable,
  ModelType,
  RowDeleteAction,
  RowDuplicateAction,
  RowEditAction,
  type TableColumn,
  type TableFilter,
  useTable,
  YesNoButton
} from '@inventreedb/ui';
import { t } from '@lingui/core/macro';
import { Alert, Stack, Text } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import { useCallback, useMemo, useState } from 'react';
import { LocalizedComponent } from './locale';

/**
 * Render a custom panel with the provided context.
 * Refer to the InvenTree documentation for the context interface
 * https://docs.inventree.org/en/latest/plugins/mixins/ui/#plugin-context
 */
function HarmonizedSystemCodesPanel({
  context
}: {
  context: InvenTreePluginContext;
}) {
  const companyId: string | number | null = useMemo(() => {
    if (context.model === ModelType.company && !!context.id) {
      return context.id;
    } else {
      return null;
    }
  }, [context.model, context.id]);

  const categoryId: string | number | null = useMemo(() => {
    if (context.model === ModelType.partcategory && !!context.id) {
      return context.id;
    } else {
      return null;
    }
  }, [context.model, context.id]);

  const CODE_URL: string = '/plugin/harmonized-system-codes/';

  // Record which is selected in the table
  const [selectedRecord, setSelectedRecord] = useState<any>(null);

  // Initial form data for creating a new code
  const [initialCodeData, setInitialCodeData] = useState<any>({});

  const tableState = useTable('hs-codes', {
    initialFilters: [
      {
        name: 'active',
        value: 'true'
      }
    ]
  });

  // Form fields for the codes
  const codeFields: ApiFormFieldSet = useMemo(() => {
    return {
      code: {},
      description: {},
      category: {
        value: categoryId || undefined
      },
      country: {},
      customer: {
        filters: {
          is_customer: true
        },
        value: companyId || undefined
      },
      notes: {},
      active: {}
    };
  }, [categoryId, companyId]);

  // Form to create a new HS code
  const createCodeForm = context.forms.create({
    url: apiUrl(CODE_URL),
    title: t`Create Harmonized Code`,
    fields: codeFields,
    initialData: initialCodeData,
    table: tableState
  });

  // Form to edit an existing HS code
  const editCodeForm = context.forms.edit({
    url: apiUrl(CODE_URL, selectedRecord?.pk),
    title: t`Edit Harmonized Code`,
    fields: codeFields,
    table: tableState
  });

  // Form to delete an existing HS code
  const deleteCodeForm = context.forms.delete({
    url: apiUrl(CODE_URL, selectedRecord?.pk),
    title: t`Delete Harmonized Code`,
    table: tableState
  });

  const tableFilters: TableFilter[] = [
    {
      name: 'active',
      label: t`Active`,
      description: t`Show active harmonized system codes`
    }
  ];

  // Row actions
  const rowActions = useCallback((record: any) => {
    return [
      RowEditAction({
        onClick: () => {
          setSelectedRecord(record);
          editCodeForm?.open();
        }
      }),
      RowDuplicateAction({
        onClick: () => {
          setInitialCodeData(record);
          createCodeForm?.open();
        }
      }),
      RowDeleteAction({
        onClick: () => {
          setSelectedRecord(record);
          deleteCodeForm?.open();
        }
      })
    ];
  }, []);

  const tableColumns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: 'code',
        switchable: false,
        sortable: true
      },
      {
        accessor: 'description'
      },
      {
        accessor: 'category',
        sortable: true,
        switchable: false,
        render: (record: any) => record.category_detail?.name ?? '-'
      },
      {
        accessor: 'country',
        sortable: true,
        switchable: false
      },
      {
        accessor: 'customer',
        switchable: false,
        sortable: true,
        render: (record: any) => record.customer_detail?.name ?? '-'
      },
      {
        accessor: 'notes',
        sortable: false
      },
      {
        accessor: 'active',
        sortable: true,
        switchable: true,
        render: (record: any) => <YesNoButton value={record.active} />
      }
    ];
  }, []);

  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        tooltip={t`Add new harmonized code`}
        onClick={() => {
          setInitialCodeData({});
          createCodeForm.open();
        }}
      />
    ];
  }, []);

  return (
    <>
      {createCodeForm.modal}
      {deleteCodeForm.modal}
      {editCodeForm.modal}
      <Stack gap='xs'>
        {companyId && (
          <Alert
            color='blue'
            icon={<IconInfoCircle />}
            title={t`Customer Codes`}
          >
            <Stack gap='xs'>
              <Text size='sm'>{t`Displaying harmonized system codes associated only with this customer.`}</Text>
              <Text size='sm'>{t`These values will override any global codes for this customer.`}</Text>
            </Stack>
          </Alert>
        )}

        <InvenTreeTable
          url={CODE_URL}
          tableState={tableState}
          columns={tableColumns}
          props={{
            params: {
              in_category: categoryId || undefined,
              customer: companyId || undefined
            },
            enableDownload: true,
            rowActions: rowActions,
            tableFilters: tableFilters,
            tableActions: tableActions
          }}
          context={context}
        />
      </Stack>
    </>
  );
}

// This is the function which is called by InvenTree to render the actual panel component
export function renderHarmonizedSystemCodesPanel(
  context: InvenTreePluginContext
) {
  checkPluginVersion(context);

  return (
    <LocalizedComponent locale={context.locale}>
      <HarmonizedSystemCodesPanel context={context} />
    </LocalizedComponent>
  );
}
