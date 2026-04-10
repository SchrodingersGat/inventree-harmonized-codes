// Import for type checking
import {
  AddItemButton,
  type ApiFormFieldSet,
  apiUrl,
  checkPluginVersion,
  type InvenTreePluginContext,
  RowActions,
  RowDeleteAction,
  RowDuplicateAction,
  RowEditAction,
  SearchInput
} from '@inventreedb/ui';
import { t } from '@lingui/core/macro';
import { ActionIcon, Alert, Group, Stack, Text, Tooltip } from '@mantine/core';
import { IconInfoCircle, IconRefresh } from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { DataTable } from 'mantine-datatable';
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
    if (context.model === 'company' && !!context.id) {
      return context.id;
    } else {
      return null;
    }
  }, [context.model, context.id]);

  const CODE_URL: string = '/plugin/harmonized-system-codes/';

  const [searchTerm, setSearchTerm] = useState<string>('');

  const codesQuery = useQuery(
    {
      queryKey: ['hsCodes', searchTerm, companyId],
      queryFn: async () => {
        return (
          context.api
            ?.get(CODE_URL, {
              params: {
                customer: companyId || undefined,
                search: searchTerm
              }
            })
            .then((response) => response.data) || []
        );
      }
    },
    context.queryClient
  );

  // Record which is selected in the table
  const [selectedRecord, setSelectedRecord] = useState<any>(null);

  // Initial form data for creating a new code
  const [initialCodeData, setInitialCodeData] = useState<any>({});

  // Form fields for the codes
  const codeFields: ApiFormFieldSet = useMemo(() => {
    return {
      code: {},
      description: {},
      category: {},
      country: {},
      customer: {
        filters: {
          is_customer: true
        },
        value: companyId || undefined,
        disabled: !!companyId
      },
      notes: {}
    };
  }, [companyId]);

  // Form to create a new HS code
  const createCodeForm = context.forms.create({
    url: apiUrl(CODE_URL),
    title: t`Create Harmonized Code`,
    fields: codeFields,
    initialData: initialCodeData,
    onFormSuccess: codesQuery.refetch
  });

  // Form to edit an existing HS code
  const editCodeForm = context.forms.edit({
    url: apiUrl(CODE_URL, selectedRecord?.pk),
    title: t`Edit Harmonized Code`,
    fields: codeFields,
    onFormSuccess: codesQuery.refetch
  });

  // Form to delete an existing HS code
  const deleteCodeForm = context.forms.delete({
    url: apiUrl(CODE_URL, selectedRecord?.pk),
    title: t`Delete Harmonized Code`,
    onFormSuccess: codesQuery.refetch
  });

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

  const tableColumns: any = useMemo(() => {
    return [
      {
        accessor: 'code'
      },
      {
        accessor: 'description'
      },
      {
        accessor: 'category',
        render: (record: any) => record.category_detail?.name ?? '-'
      },
      {
        accessor: 'country'
      },
      {
        accessor: 'customer',
        render: (record: any) => record.customer_detail?.name ?? '-'
      },
      {
        accessor: 'notes'
      },
      {
        accessor: '---',
        title: ' ',
        width: 50,
        resizable: false,
        sortable: false,
        render: (record: any, index: number) => (
          <RowActions actions={rowActions(record)} index={index} />
        )
      }
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
        <Group justify='space-between'>
          <Group gap='xs'>
            <AddItemButton
              tooltip={t`Add new harmonized code`}
              onClick={() => {
                setInitialCodeData({});
                createCodeForm.open();
              }}
            />
          </Group>
          <Group gap='xs'>
            <SearchInput
              searchCallback={(value: string) => {
                setSearchTerm(value);
              }}
            />
            <Tooltip label='Refresh data' position='top-end'>
              <ActionIcon
                variant='transparent'
                onClick={() => {
                  codesQuery.refetch();
                }}
              >
                <IconRefresh />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Group>
        <DataTable
          minHeight={250}
          withTableBorder
          withColumnBorders
          idAccessor='pk'
          noRecordsText={t`No Harmonized System Codes found`}
          fetching={codesQuery.isFetching || codesQuery.isLoading}
          columns={tableColumns}
          records={codesQuery.data || []}
          pinLastColumn
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
